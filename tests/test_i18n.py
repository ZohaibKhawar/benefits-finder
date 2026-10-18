"""French: nothing untranslated, placeholders kept, numbers and dates written the French way."""

import re

import pytest

from app import app
from finder.i18n import Money, Month, Msg, catalog, money, month
from finder.i18n_keys import missing


def test_every_sentence_has_a_french_translation():
    ui, benefits = missing("fr")
    assert ui == [], f"untranslated: {ui[:5]}"
    assert benefits == [], f"untranslated benefit fields: {benefits[:5]}"


def test_translations_keep_their_placeholders():
    for english, french in catalog("fr")["text"].items():
        assert sorted(re.findall(r"\{\w+\}", english)) == sorted(re.findall(r"\{\w+\}", french)), english


def test_french_money_and_months():
    assert money(1402, "fr") == "1 402 $"
    assert money(1402, "en") == "$1,402"
    assert month(Month(2027, 3, 1), "fr") == "mars 2027"


def test_messages_render_in_french():
    message = Msg("Worked out from a family income of about {income}.", income=Money(9000))
    assert str(message) == "Worked out from a family income of about $9,000."
    assert message.render("fr") == "Calculé à partir d'un revenu familial d'environ 9 000 $."


@pytest.fixture
def client():
    return app.test_client()


def test_french_pages(client):
    home = client.get("/fr/").get_data(as_text=True)
    assert '<html lang="fr">' in home
    assert "Trouvez les prestations qui vous échappent" in home
    quiz = client.get("/fr/start").get_data(as_text=True)
    assert "Quel âge avez-vous?" in quiz
    assert 'action="/fr/results"' in quiz


def test_french_results(client):
    form = {"province": "ON", "city": "toronto", "age": "20", "status": "citizen", "arrived_when": "long_ago",
            "student": "full_time", "school_type": "public", "housing": "rent", "monthly_rent": "900",
            "has_partner": "no", "work_income": "9000", "has_dental_plan": "1", "has_drug_plan": "1",
            "disability": "no", "filed_taxes": "yes"}
    page = client.post("/fr/results", data=form).get_data(as_text=True)
    assert "1 402 $" in page
    assert "Allocation canadienne pour l'épicerie et les besoins essentiels" in page or \
           "Allocation canadienne pour l&#39;épicerie et les besoins essentiels" in page
    assert "Produisez votre déclaration de revenus de 2026 d&#39;ici le 30 avril 2027" in page
    assert "Probable" in page
