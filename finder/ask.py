"""Optional "ask about your results" helper, answered by Claude.

Off unless ANTHROPIC_API_KEY is set on the server. It only explains the results the rules engine
already worked out; it never decides who qualifies. Nothing is stored: the question and a short
summary of the results go to Anthropic for one answer.

Cost: Claude Haiku 5.5 is $0.10 per million input tokens and $0.50 per million output tokens,
so one question (about 1,500 tokens in, up to 700 out) costs well under a tenth of a cent.
"""

import os
import threading
import time
from collections import deque

import anthropic

from .engine import Report
from .i18n import benefit_text, money, render

MODEL = os.environ.get("BENEFITS_AI_MODEL", "claude-haiku-5-5")
MAX_QUESTION_CHARS = 500
PER_VISITOR_PER_HOUR = 8
SITE_PER_DAY = int(os.environ.get("BENEFITS_AI_DAILY_LIMIT", "500"))

SYSTEM_PROMPT = """You help people understand a page of Canadian government benefits that a \
rules engine already worked out for them. The page lists each benefit, whether they likely, \
maybe, or don't yet qualify, the reason, a rough amount, and how to apply.

Answer only from the results you're given and general, well-known facts about how these \
programs work. Don't change who qualifies: if they ask whether they qualify for something, \
repeat what the results say and point to the official page. Don't give tax, legal or \
immigration advice; for those, suggest a free tax clinic, a legal clinic or a settlement agency. \
If the question isn't about benefits, money help, taxes or applying, say briefly that you can \
only help with their results.

Write in plain words for someone who may be reading in a second language: short sentences, \
no jargon, under 150 words. Answer in {language}."""

LANGUAGE_NAMES = {"en": "English", "fr": "Canadian French"}


class AskError(Exception):
    """A problem to show the person, in their language (the message is the English key)."""


def enabled() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(timeout=30.0, max_retries=2)
    return _client


# ------------------------------------------------------------------ spending limits
# Kept in memory only: visitor keys are forgotten after an hour and never written anywhere.

_lock = threading.Lock()
_recent: dict[str, deque] = {}
_today: list = [None, 0]


def allow(visitor: str, now: float | None = None) -> bool:
    now = time.time() if now is None else now
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    with _lock:
        if _today[0] != day:
            _today[:] = [day, 0]
            _recent.clear()
        if _today[1] >= SITE_PER_DAY:
            return False
        times = _recent.setdefault(visitor, deque())
        while times and now - times[0] > 3600:
            times.popleft()
        if len(times) >= PER_VISITOR_PER_HOUR:
            return False
        times.append(now)
        _today[1] += 1
        return True


# ------------------------------------------------------------------ the question

def results_summary(report: Report, lang: str) -> str:
    """The results page as short plain text, the only personal context Claude sees."""
    lines = [f"Province: {report.province}"]
    for item in report.items:
        amount = ""
        if item.estimate:
            amount = f", about {money(item.estimate, lang)} a year"
        elif item.up_to:
            amount = f", up to {money(item.up_to, lang)}"
        when = f", from {render(item.available_from, lang)}" if item.available_from else ""
        reasons = " ".join(render(reason, lang) for reason in item.reasons)
        lines.append(f"- {benefit_text(item.benefit, 'name', lang)}: {item.status}{amount}{when}. {reasons}")
    lines.append("Plan:")
    lines += [f"{n}. {render(step.text, lang)}" for n, step in enumerate(report.plan, 1)]
    return "\n".join(lines)


def ask(question: str, report: Report, lang: str) -> str:
    question = (question or "").strip()
    if not question:
        raise AskError("Type a question first.")
    if len(question) > MAX_QUESTION_CHARS:
        raise AskError("Please keep your question under 500 characters.")
    try:
        response = client().messages.create(
            model=MODEL,
            max_tokens=1024,
            output_config={"effort": "low"},
            system=SYSTEM_PROMPT.format(language=LANGUAGE_NAMES.get(lang, "English")),
            messages=[{
                "role": "user",
                "content": f"<results>\n{results_summary(report, lang)}\n</results>\n\n"
                           f"<question>\n{question}\n</question>",
            }],
        )
    except anthropic.RateLimitError:
        raise AskError("The helper is busy right now. Try again in a minute.") from None
    except (anthropic.APIConnectionError, anthropic.APITimeoutError):
        raise AskError("We couldn't reach the helper. Try again in a minute.") from None
    except anthropic.APIStatusError:
        raise AskError("The helper isn't working right now. Your results above are still correct.") from None

    if response.stop_reason == "refusal":
        raise AskError("The helper can't answer that one. Try asking about a benefit on your list.")
    text = "\n".join(block.text for block in response.content if block.type == "text").strip()
    if not text:
        raise AskError("The helper isn't working right now. Your results above are still correct.")
    return text
