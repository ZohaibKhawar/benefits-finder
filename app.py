"""Claimable website (the code and repository are still called benefits-finder).

Every page exists in English at / and in French at /fr/. Answers arrive by POST, are used to
build the results page, and are never saved or logged.

Run locally: python app.py  (http://127.0.0.1:5240)
"""

import os
from datetime import date

from flask import Blueprint, Flask, Response, abort, redirect, render_template, request, url_for

from finder import ask as helper
from finder import find
from finder.calendar import build_calendar
from finder.data import PROVINCE_FILES, all_benefits, load
from finder.engine import GROUPS
from finder.form import QUESTIONS, FormError, answers_from_form, answers_from_json, answers_to_json, form_values
from finder.i18n import LANGUAGES, Msg, benefit_text, gettext, money, render
from finder.samples import PEOPLE

APP_NAME = "Claimable"   # not "Benefits Finder": that is the Government of Canada's own tool
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:5240").rstrip("/")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "")   # privacy questions and mistakes; set it before going live

app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600   # CSS, JS and icon: cache for an hour
pages = Blueprint("pages", __name__)

STATUS_LABELS = {"likely": "Likely", "maybe": "Maybe", "not_yet": "Not yet", "no": "Probably not"}

WHATS_NEW = [
    Msg("The GST/HST credit is now the Canada Groceries and Essentials Benefit, and it's 25% bigger until 2031."),
    Msg("In Ontario, most provincial student aid is now a loan, not a grant (since August 1, 2026). The federal grant is still free."),
    Msg("The Canadian Dental Care Plan is open to every age, if you have no dental insurance."),
    Msg("Health card waits differ: Ontario has none, while BC and Quebec make most newcomers wait about 3 months."),
]


def lang() -> str:
    return "fr" if request.blueprint == "fr" else "en"


def link(endpoint: str, **values) -> str:
    return url_for(f"{lang()}.{endpoint}", **values)


def language_urls() -> dict:
    """This page's address in each language, for hreflang and canonical tags (GET pages only)."""
    endpoint = (request.endpoint or "en.home").split(".")[-1]
    if request.method != "GET" or request.blueprint not in LANGUAGES:
        endpoint = "home"
    return {code: SITE_URL + url_for(f"{code}.{endpoint}", **(request.view_args or {})) for code in LANGUAGES}


def other_language_url() -> str:
    other = "en" if lang() == "fr" else "fr"
    endpoint = (request.endpoint or "en.home").split(".")[-1]
    if request.method != "GET" or endpoint in ("results", "calendar"):
        endpoint = "home"
    return url_for(f"{other}.{endpoint}", **(request.view_args or {}))


@app.context_processor
def template_helpers():
    current = lang() if request.blueprint in LANGUAGES else "en"

    def _(text, **values):
        translated = gettext(text, current)
        return translated.format(**values) if values else translated

    return {
        "lang": current,
        "_": _,
        "r": lambda value: render(value, current),
        "bt": lambda benefit, field: benefit_text(benefit, field, current),
        "money": lambda amount: money(amount, current),
        "link": link,
        "other_language_url": other_language_url,
        "language_urls": language_urls,
        "app_name": APP_NAME,
        "site_url": SITE_URL,
        "status_labels": STATUS_LABELS,
        "ai_enabled": helper.enabled(),
        "contact_email": CONTACT_EMAIL,
    }


@app.after_request
def security_headers(response):
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' https://fonts.googleapis.com; "
        "font-src https://fonts.gstatic.com; img-src 'self' data:; script-src 'self'; "
        "connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"   # browsers ignore it over plain http
    if request.method == "POST":
        response.headers["Cache-Control"] = "no-store"   # results never sit in a shared computer's cache
    return response


# ------------------------------------------------------------------ pages

@pages.route("/")
def home():
    example = find(PEOPLE["aisha"])
    return render_template("home.html", example=example, whats_new=WHATS_NEW)


@pages.route("/start", methods=["GET", "POST"])
def quiz():
    values = {}
    if request.method == "POST" and request.form.get("answers"):
        try:
            values = form_values(answers_from_json(request.form["answers"]))
        except ValueError:
            values = {}
    return render_template("quiz.html", questions=QUESTIONS, values=values, errors={})


@pages.route("/results", methods=["GET", "POST"])
def results():
    if request.method == "GET":
        return redirect(link("quiz"))
    try:
        answers = answers_from_form(request.form)
    except FormError as error:
        return render_template("quiz.html", questions=QUESTIONS, values=request.form.to_dict(),
                               errors={error.field: error.message}), 400
    report = find(answers)
    return render_template("results.html", report=report, answers=answers,
                           answers_json=answers_to_json(answers), groups=GROUPS)


@pages.route("/ask", methods=["POST"])
def ask_question():
    if not helper.enabled():
        abort(404)
    try:
        answers = answers_from_json(request.form.get("answers", ""))
    except ValueError:
        abort(400)
    report = find(answers)
    question = request.form.get("question", "")[:2000]
    answer = error = None
    visitor = request.headers.get("X-Real-IP") or request.remote_addr or "unknown"
    if not question.strip():
        error = "Type a question first."
    elif not helper.allow(visitor):
        error = "The helper has answered a lot of questions recently. Try again later."
    else:
        try:
            answer = helper.ask(question, report, lang())
        except helper.AskError as problem:
            error = str(problem)
    return render_template("results.html", report=report, answers=answers,
                           answers_json=answers_to_json(answers), groups=GROUPS,
                           ask_question=question, ask_answer=answer, ask_error=error)


@pages.route("/calendar.ics", methods=["POST"])
def calendar():
    try:
        answers = answers_from_json(request.form.get("answers", ""))
    except ValueError:
        abort(400)
    report = find(answers)
    body = build_calendar(report, lang(), link_base=SITE_URL + link("home"))
    return Response(body, mimetype="text/calendar",
                    headers={"Content-Disposition": 'attachment; filename="benefit-dates.ics"'})


@pages.route("/benefits")
def benefits():
    provinces = {code: load(code)[0] for code in PROVINCE_FILES}
    return render_template("benefits.html", provinces=provinces, groups=GROUPS)


@pages.route("/benefits/<benefit_id>")
def benefit(benefit_id):
    entry = all_benefits().get(benefit_id)
    if entry is None:
        abort(404)
    return render_template("benefit.html", benefit=entry, groups=dict(GROUPS))


@pages.route("/about")
def about():
    return render_template("about.html")


@pages.route("/privacy")
def privacy():
    return render_template("privacy.html")


app.register_blueprint(pages, name="en")
app.register_blueprint(pages, url_prefix="/fr", name="fr")


# ------------------------------------------------------------------ site files

@app.route("/robots.txt")
def robots():
    body = "User-agent: *\nDisallow: /results\nDisallow: /fr/results\nAllow: /\n"
    return Response(f"{body}Sitemap: {SITE_URL}/sitemap.xml\n", mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    paths = ["/", "/start", "/benefits", "/about", "/privacy"]
    paths += [f"/benefits/{benefit_id}" for benefit_id in all_benefits()]
    urls = [f"{SITE_URL}{prefix}{path}" for prefix in ("", "/fr") for path in paths]
    today = date.today().isoformat()
    body = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    body += [f"<url><loc>{url}</loc><lastmod>{today}</lastmod></url>" for url in urls]
    body.append("</urlset>")
    return Response("\n".join(body), mimetype="application/xml")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5240)), debug=bool(os.environ.get("DEBUG")))
