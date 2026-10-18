"""The optional AI helper, tested with a fake Claude client (no real calls, no cost)."""

import html
import re
from types import SimpleNamespace

import pytest

from app import app
from finder import ask as helper

AISHA = {
    "province": "ON", "city": "toronto", "age": "20", "status": "citizen", "arrived_when": "long_ago",
    "student": "full_time", "school_type": "public", "housing": "rent", "monthly_rent": "900",
    "has_partner": "no", "work_income": "9000", "has_dental_plan": "1", "has_drug_plan": "1",
    "disability": "no", "filed_taxes": "yes",
}


class FakeMessages:
    def __init__(self, reply="Because you study full-time.\n\nPart-time students can get it.", stop="end_turn",
                 error=None):
        self.reply, self.stop, self.error, self.calls = reply, stop, error, []

    def create(self, **request):
        self.calls.append(request)
        if self.error:
            raise self.error
        return SimpleNamespace(stop_reason=self.stop, content=[SimpleNamespace(type="text", text=self.reply)])


@pytest.fixture
def fake(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    messages = FakeMessages()
    monkeypatch.setattr(helper, "_client", SimpleNamespace(messages=messages))
    helper._recent.clear()
    helper._today[:] = [None, 0]
    return messages


def answers_json(client, prefix=""):
    page = client.post(f"{prefix}/results", data=AISHA).get_data(as_text=True)
    return html.unescape(re.search(r'name="answers" value="([^"]+)"', page).group(1))


def test_helper_is_hidden_without_a_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = app.test_client()
    assert "Ask about your results" not in client.post("/results", data=AISHA).get_data(as_text=True)
    assert client.post("/ask", data={"answers": "{}", "question": "hi"}).status_code == 404


def test_question_gets_an_answer(fake):
    client = app.test_client()
    page = client.post("/ask", data={"answers": answers_json(client), "question": "Why no CWB?"}).get_data(as_text=True)
    assert "Because you study full-time." in page
    assert "<p>Part-time students can get it.</p>" in page
    request = fake.calls[0]
    assert request["model"] == "claude-haiku-5-5"
    assert request["output_config"] == {"effort": "low"}
    assert "Answer in English." in request["system"]
    assert "Canada Workers Benefit: no" in request["messages"][0]["content"]
    assert "<question>\nWhy no CWB?\n</question>" in request["messages"][0]["content"]


def test_french_questions_get_french_instructions(fake):
    client = app.test_client()
    client.post("/fr/ask", data={"answers": answers_json(client, "/fr"), "question": "Pourquoi?"})
    assert "Answer in Canadian French." in fake.calls[0]["system"]
    assert "Allocation canadienne pour les travailleurs: no" in fake.calls[0]["messages"][0]["content"]


def test_empty_and_long_questions_are_stopped_before_calling_claude(fake):
    client = app.test_client()
    answers = answers_json(client)
    assert "Type a question first." in client.post("/ask", data={"answers": answers, "question": " "}).get_data(as_text=True)
    page = client.post("/ask", data={"answers": answers, "question": "x" * 600}).get_data(as_text=True)
    assert "under 500 characters" in page
    assert fake.calls == []


def test_refusals_and_errors_show_a_plain_message(fake):
    client = app.test_client()
    answers = answers_json(client)
    fake.stop = "refusal"
    assert "can&#39;t answer that one" in client.post("/ask", data={"answers": answers, "question": "q"}).get_data(as_text=True)
    fake.stop, fake.error = "end_turn", helper.anthropic.APIConnectionError(request=None)
    assert "couldn&#39;t reach the helper" in client.post("/ask", data={"answers": answers, "question": "q"}).get_data(as_text=True)


def test_each_visitor_is_limited_per_hour(fake):
    for _ in range(helper.PER_VISITOR_PER_HOUR):
        assert helper.allow("1.2.3.4", now=1000)
    assert not helper.allow("1.2.3.4", now=1000)
    assert helper.allow("5.6.7.8", now=1000)
    assert helper.allow("1.2.3.4", now=1000 + 3601)
