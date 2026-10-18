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


def test_calendar_download(client):
    page = client.post("/results", data=AISHA).get_data(as_text=True)
    answers = html.unescape(re.search(r'name="answers" value="([^"]+)"', page).group(1))
    response = client.post("/calendar.ics", data={"answers": answers})
    body = response.get_data(as_text=True)
    assert response.mimetype == "text/calendar"
    assert "BEGIN:VCALENDAR" in body and "DTSTART;VALUE=DATE:" in body
    assert "\r\n" in body


def test_calendar_rejects_junk(client):
    assert client.post("/calendar.ics", data={"answers": "not json"}).status_code == 400


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


def test_answers_never_go_in_a_url(client):
    page = client.get("/start").get_data(as_text=True)
    assert 'method="post"' in page
    assert 'method="get"' not in page.lower()


def test_language_switch_points_to_the_other_language(client):
    assert 'href="/fr/"' in client.get("/").get_data(as_text=True)
    assert 'href="/"' in client.get("/fr/").get_data(as_text=True)
