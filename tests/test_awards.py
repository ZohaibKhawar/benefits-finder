"""Scholarships and bursaries for Ontario students: trusted links only, grade scales, matching, entrance
scholarships and the pages."""

import html
import re
from datetime import date

import pytest

from app import app
from finder import awards as A
from finder.i18n import Percent, money, percent


# ---------------------------------------------------------------- the data and its links

def test_every_link_is_https_and_on_a_trusted_site():
    trusted = A.trusted_domains()
    for award in A.awards().values():
        assert award["url"].startswith("https://"), award["id"]
        assert any(A.on_domain(award["url"], domain) for domain in trusted), f"{award['id']}: {award['url']}"


def test_every_school_link_is_on_the_schools_own_site():
    for school in A.schools().values():
        urls = [school["url"]] + ([school["entrance"]["url"]] if "entrance" in school else [])
        for url in urls:
            assert url.startswith("https://"), school["id"]
            assert A.on_domain(url, school["domain"]), f"{school['id']}: {url}"


def test_a_lookalike_domain_is_not_trusted():
    assert A.on_domain("https://www.ontario.ca/page/x", "ontario.ca")
    assert not A.on_domain("https://fakeontario.ca/page/x", "ontario.ca")
    assert not A.on_domain("https://ontario.ca.scholarships.example/x", "ontario.ca")


def test_every_public_school_is_listed():
    kinds = [school["kind"] for school in A.schools().values()]
    assert kinds.count("college") == 24
    assert kinds.count("university") >= 23


def test_entrance_tiers_go_from_highest_to_lowest():
    for school in A.schools().values():
        tiers = school.get("entrance", {}).get("tiers", [])
        assert [t["min"] for t in tiers] == sorted((t["min"] for t in tiers), reverse=True), school["id"]
        for tier in tiers:
            assert tier.get("first_year") or tier.get("total"), school["id"]
            assert not tier.get("total") or tier["total"] >= tier.get("first_year", 0), school["id"]


def test_nothing_is_more_than_a_year_old():
    for entry in [*A.schools().values(), *A.awards().values()]:
        assert (date.today() - entry["last_checked"]).days < 365, entry["id"]


def test_ended_programs_are_not_listed():
    names = " ".join(award["name"].lower() for award in A.awards().values())
    assert "td scholarship" not in names            # ended in 2025
    assert "apprenticeship incentive grant" not in names   # closed March 31, 2025


# ---------------------------------------------------------------- grades on every scale

@pytest.mark.parametrize("grade, scale, expected", [
    (91, "percent", 91), (4.0, "4", 85), (3.7, "4", 80), (3.5, "4", 77), (4.33, "4.33", 90),
    (8, "9", 80), (7.5, "9", 75), (9, "10", 85), (11, "12", 85), (10.5, "12", 80), (0, "12", 0),
])
def test_grades_convert_to_the_bottom_of_their_letter(grade, scale, expected):
    assert A.to_percent(grade, scale) == expected


def test_percent_is_written_the_french_way():
    assert percent(88, "en") == "88%"
    assert percent(77.5, "fr") == "77,5 %"
    assert str(A.Msg("At least {needed}.", needed=Percent(80))) == "At least 80%."


def student(**changes):
    values = {"school": "carleton", "level": "bachelor", "year": "second", "field": "stem", "grade": 82,
              "status": "citizen", "need": "osap"}
    return A.Student(**{**values, **changes})


@pytest.mark.parametrize("bad", [{"school": "harvard"}, {"level": "kindergarten"}, {"grade": 101},
                                 {"grade": 13, "scale": "12"}, {"grade": "high"}, {"identities": ("wizard",)}])
def test_bad_answers_are_rejected(bad):
    with pytest.raises(ValueError):
        student(**bad)


# ---------------------------------------------------------------- matching

def by_id(report):
    return {m.id: m for m in report.matches}


def test_first_generation_student_with_need_fits():
    found = by_id(A.find_awards(student(identities=("first_gen",))))
    assert found["first_generation"].status == "check"      # residency and first program are on them to check
    assert "first_generation" not in by_id(A.find_awards(student()))   # hidden from everyone else


def test_bursaries_need_need():
    found = by_id(A.find_awards(student(identities=("first_gen",), need="no")))
    assert found["first_generation"].status == "no"
    assert "need money" in found["first_generation"].reasons[0]


def test_international_students_are_told_why_not():
    found = by_id(A.find_awards(student(identities=("first_gen",), status="study_permit")))
    assert found["first_generation"].status == "no"
    assert "citizens, permanent residents and protected persons" in found["first_generation"].reasons[0]
    assert found["educanada"].status == "fits"             # and pointed to the international search
    assert "educanada" not in by_id(A.find_awards(student()))


def test_indigenous_students_see_their_own_programs():
    metis = by_id(A.find_awards(student(identities=("metis",))))
    assert {"indigenous_student_bursary", "mno_bursary", "indspire", "isc_search"} <= set(metis)
    assert "psssp" not in metis and "inuit_strategy" not in metis
    first_nations = by_id(A.find_awards(student(identities=("first_nations",))))
    assert {"psssp", "fnrds", "indspire"} <= set(first_nations) and "mno_bursary" not in first_nations


def test_average_cutoffs():
    low = by_id(A.find_awards(student(year="hs_senior", grade=85)))
    assert low["loran"].status == "no"
    assert "88%" in low["loran"].reasons[0] and "85%" in low["loran"].reasons[0]
    unknown = by_id(A.find_awards(student(year="hs_senior", grade=None)))
    assert unknown["loran"].status == "check"
    assert any("at least 88%" in reason for reason in unknown["loran"].reasons)


def test_a_converted_gpa_is_used_for_cutoffs():
    found = by_id(A.find_awards(student(level="bachelor", year="fourth_plus", grade=3.7, scale="4")))
    assert found["cgrs_m"].status == "check"        # 3.7/4.0 is an A-, 80%: meets the bar, with the A- note
    found = by_id(A.find_awards(student(level="bachelor", year="fourth_plus", grade=3.3, scale="4")))
    assert found["cgrs_m"].status == "no"


def test_awards_for_other_levels_and_fields_stay_hidden():
    found = by_id(A.find_awards(student(year="second")))
    assert "cgrs_m" not in found and "ogs" not in found and "loran" not in found
    assert "cnf" not in found                                     # nursing only
    assert "cnf" in by_id(A.find_awards(student(field="health")))
    assert "schulich_builders" in by_id(A.find_awards(student(level="college", field="trades", year="hs_senior")))


def test_activities_unlock_and_shape_matches():
    assert "usra" not in by_id(A.find_awards(student()))
    assert by_id(A.find_awards(student(activities=("research",))))["usra"].status == "check"
    quiet = by_id(A.find_awards(student(year="hs_senior", grade=92)))["loran"]
    involved = by_id(A.find_awards(student(year="hs_senior", grade=92, activities=("volunteer",))))["loran"]
    assert len(quiet.reasons) == len(involved.reasons) + 1      # the "they look for service" note goes away


def test_black_students_see_their_awards():
    found = by_id(A.find_awards(student(identities=("black",), field="social", activities=("research",))))
    assert {"bbpa", "usra_black"} <= set(found)
    assert found["bbpa"].status == "check"                      # age 17 to 30


# ---------------------------------------------------------------- entrance scholarships

def test_entrance_scholarship_at_the_students_average():
    offer = A.entrance(A.schools()["carleton"], student(year="hs_senior", grade=91))
    assert offer.status == "amount" and offer.tier == {"min": 90, "first_year": 2000, "total": 8000}
    assert A.entrance(A.schools()["carleton"], student(year="hs_senior", grade=84)).status == "below"
    assert A.entrance(A.schools()["carleton"], student(year="hs_senior", grade=None)).status == "unknown_average"


def test_entrance_scholarships_are_for_new_degree_students_from_canada():
    carleton = A.schools()["carleton"]
    assert A.entrance(carleton, student(year="second")) is None
    assert A.entrance(carleton, student(level="college", year="hs_senior")) is None
    assert A.entrance(carleton, student(year="first")).status == "decided"
    assert A.entrance(carleton, student(year="hs_senior", status="study_permit")).status == "not_eligible"
    assert A.entrance(A.schools()["guelph"], student(year="hs_senior", grade=96, status="protected")).status == "not_eligible"
    assert A.entrance(A.schools()["queens"], student(year="hs_senior", grade=93)).status == "qualifies"


def test_entrance_table_compares_every_university():
    rows = A.entrance_table(student(year="hs_senior", grade=96))
    names = [row.school["name"] for row in rows]
    assert names[0] == "Trent University"                      # free first-year tuition at 95%
    assert "Carleton University" in names and "Algonquin College" not in names
    firsts = [row.tier.get("first_year") or 0 for row in rows if row.tier]
    assert firsts == sorted(firsts, reverse=True)
    assert A.entrance_table(student(year="second", grade=96)) == []


# ---------------------------------------------------------------- pages

FORM = {"school": "york", "level": "bachelor", "field": "stem", "year": "hs_senior", "grade": "87",
        "scale": "percent", "status": "citizen", "need": "osap", "first_gen": "1", "volunteer": "1"}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


@pytest.mark.parametrize("path", ["/awards", "/fr/awards", "/awards/sources", "/fr/awards/sources"])
def test_pages_load(client, path):
    assert client.get(path).status_code == 200


def test_results(client):
    response = client.post("/awards/results", data=FORM)
    page = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert "At York University" in page
    assert "$1,500 in first year, up to $6,000 in all" in page
    assert "Ontario First Generation Bursary" in page
    assert "Watch out for scholarship scams" in page


def test_results_in_french(client):
    page = client.post("/fr/awards/results", data=FORM).get_data(as_text=True)
    assert '<html lang="fr">' in page
    assert f"{money(1500, 'fr')} la première année" in page
    assert "Bourse ontarienne pour les étudiantes et étudiants de première génération" in page


def test_results_need_a_post(client):
    assert client.get("/awards/results").status_code == 302


@pytest.mark.parametrize("change, field, message", [
    ({"school": ""}, "school", "Pick your school"),
    ({"grade": "lots"}, "grade", "Enter a number"),
    ({"grade": "5", "scale": "4"}, "grade", "higher than the scale goes"),
])
def test_bad_answers_go_back_to_the_question(client, change, field, message):
    response = client.post("/awards/results", data={**FORM, **change})
    page = response.get_data(as_text=True)
    assert response.status_code == 400
    assert message in page
    assert f'id="{field}-error"' in page


def test_change_my_answers_prefills_the_form(client):
    page = client.post("/awards/results", data=FORM).get_data(as_text=True)
    answers = html.unescape(re.search(r'name="answers" value="([^"]+)"', page).group(1))
    quiz = client.post("/awards", data={"answers": answers}).get_data(as_text=True)
    assert '<option value="york" selected>' in quiz
    assert 'value="87"' in quiz
    assert re.search(r'name="first_gen" value="1"\s+checked', quiz)


@pytest.mark.parametrize("junk", ["not json", "[]", '{"school": "harvard"}', '{"grade": "A+"}',
                                  '{"identities": ["wizard"]}'])
def test_tampered_answers_give_a_blank_form_not_a_crash(client, junk):
    assert client.post("/awards", data={"answers": junk}).status_code == 200


def test_every_link_on_a_results_page_is_trusted(client):
    page = client.post("/awards/results", data={**FORM, "metis": "1", "black": "1", "disability": "1",
                                                 "care": "1", "military_family": "1"}).get_data(as_text=True)
    domains = [*A.trusted_domains(), *(school["domain"] for school in A.schools().values())]
    main = page.split('<main id="main">')[1].split("</main>")[0]
    urls = re.findall(r'<a [^>]*href="(https?://[^"]+)"', main)
    assert len(urls) > 10
    for url in urls:
        assert any(A.on_domain(url, domain) for domain in domains), url


def test_results_pages_stay_out_of_search_engines(client):
    assert "Disallow: /awards/results" in client.get("/robots.txt").get_data(as_text=True)
    assert "/awards/sources" in client.get("/sitemap.xml").get_data(as_text=True)


def test_benefits_results_point_ontario_students_here(client):
    form = {"province": "ON", "city": "toronto", "age": "20", "student": "full_time", "school_type": "public",
            "housing": "rent", "monthly_rent": "900", "work_income": "9000"}
    assert 'href="/awards"' in client.post("/results", data=form).get_data(as_text=True)
    assert 'href="/awards"' not in client.post("/results", data={**form, "province": "BC"}).get_data(as_text=True).split("<footer")[0]
