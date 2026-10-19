"""The website: every page loads, the questionnaire turns into results, nothing leaks into URLs."""

import html
import re

import pytest

from app import app
from finder.data import all_benefits

AISHA = {
    "province": "ON", "city": "toronto", "age": "20", "status": "citizen", "arrived_when": "long_ago",
    "student": "full_time", "school_type": "public", "housing": "rent", "monthly_rent": "900",
    "has_partner": "no", "work_income": "9,000", "other_income": "", "has_dental_plan": "1",
    "has_drug_plan": "1", "disability": "no", "filed_taxes": "yes",
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize("path", ["/", "/start", "/benefits", "/about", "/privacy", "/benefits/cgeb",
                                  "/fr/", "/fr/start", "/fr/benefits", "/robots.txt", "/sitemap.xml"])
def test_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_every_benefit_has_a_page(client):
    for benefit_id in all_benefits():
        assert client.get(f"/benefits/{benefit_id}").status_code == 200


def test_unknown_pages_are_404(client):
    assert client.get("/benefits/not-a-benefit").status_code == 404
    assert client.get("/nope").status_code == 404


def test_results_from_the_questionnaire(client):
    response = client.post("/results", data=AISHA)
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert '<mark class="highlight">$1,402</mark>' in page
    assert "Ontario Energy and Property Tax Credit" in page
    assert "File your" in page
    assert response.headers["Cache-Control"] == "no-store"


def test_results_need_a_post(client):
    response = client.get("/results?age=20")
    assert response.status_code == 302


def test_missing_age_goes_back_to_the_question(client):
    response = client.post("/results", data={**AISHA, "age": ""})
    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "Enter your age." in page
    assert 'id="screen-age" data-start' in page


def test_bad_numbers_are_caught(client):
    response = client.post("/results", data={**AISHA, "work_income": "lots"})
    assert response.status_code == 400
    assert "Enter a number" in response.get_data(as_text=True)


def test_recent_arrival_needs_a_month(client):
    response = client.post("/results", data={**AISHA, "arrived_when": "recent", "arrived_month": ""})
    assert response.status_code == 400


@pytest.mark.parametrize("month, message", [("March 2025", "Enter the month like 2025-03."),
                                            ("0000-01", "Enter the month like 2025-03."),
                                            ("2099-01", "That month hasn&#39;t happened yet.")])
def test_arrival_month_must_be_real(client, month, message):
    response = client.post("/results", data={**AISHA, "arrived_when": "recent", "arrived_month": month})
    assert response.status_code == 400
    assert message in response.get_data(as_text=True)


def test_calendar_download(client):
    page = client.post("/results", data=AISHA).get_data(as_text=True)
    answers = html.unescape(re.search(r'name="answers" value="([^"]+)"', page).group(1))
    response = client.post("/calendar.ics", data={"answers": answers})
    body = response.get_data(as_text=True)
    assert response.mimetype == "text/calendar"
    assert "BEGIN:VCALENDAR" in body and "DTSTART;VALUE=DATE:" in body
    assert "\r\n" in body


@pytest.mark.parametrize("junk", ["not json", "{}", '{"age": "20"}', '{"age": 20, "work_income": NaN}',
                                  '{"age": 20, "arrived": 5}', '{"age": 20, "kids_under_6": "two"}'])
def test_tampered_answers_are_rejected_not_crashes(client, junk):
    assert client.post("/calendar.ics", data={"answers": junk}).status_code == 400
    assert client.post("/start", data={"answers": junk}).status_code == 200   # a blank questionnaire


def test_change_my_answers_prefills_the_form(client):
    page = client.post("/results", data=AISHA).get_data(as_text=True)
    answers = html.unescape(re.search(r'name="answers" value="([^"]+)"', page).group(1))
    quiz = client.post("/start", data={"answers": answers}).get_data(as_text=True)
    assert 'value="20"' in quiz
    assert 'name="city" value="toronto" checked' in quiz


def test_security_headers(client):
    headers = client.get("/").headers
    assert "default-src 'self'" in headers["Content-Security-Policy"]
    assert headers["Referrer-Policy"] == "no-referrer"
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Strict-Transport-Security"].startswith("max-age=")


def test_privacy_contact_shows_once_set(client, monkeypatch):
    assert "mailto:" not in client.get("/privacy").get_data(as_text=True)
    monkeypatch.setattr("app.CONTACT_EMAIL", "hello@example.org")
    page = client.get("/fr/privacy").get_data(as_text=True)
    assert "écrivez à hello@example.org" in page and 'href="mailto:hello@example.org"' in page


def test_answers_never_go_in_a_url(client):
    page = client.get("/start").get_data(as_text=True)
    assert 'method="post"' in page
    assert 'method="get"' not in page.lower()


def test_language_switch_points_to_the_other_language(client):
    assert 'href="/fr/"' in client.get("/").get_data(as_text=True)
    assert 'href="/"' in client.get("/fr/").get_data(as_text=True)


@pytest.mark.parametrize("path", ["/", "/fr/", "/about", "/fr/about", "/benefits", "/privacy"])
def test_site_never_uses_the_government_tool_name(client, path):
    page = client.get(path).get_data(as_text=True)
    assert "Benefits Finder" not in page and "Claimable" in page
