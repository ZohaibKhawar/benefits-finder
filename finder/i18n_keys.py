"""Lists every English sentence the site can show, so a test can check each has a translation.

Run: python -m finder.i18n_keys fr     (prints what's missing from translations/fr.yaml)
"""

import ast
import re
import sys
from pathlib import Path

from .data import PROVINCE_FILES, all_benefits, load
from .engine import GROUPS
from .form import QUESTIONS
from .i18n import catalog

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_CALL = re.compile(r"""_\(\s*(["'])((?:(?!\1).)*)\1""")
CALLS_WITH_TEXT = {"Msg": 0, "gettext": 0, "FormError": 1, "AskError": 0}
PARAM_TEXTS = ("wait", "study_note", "note")


def _from_python(path: Path) -> set[str]:
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            index = CALLS_WITH_TEXT.get(name)
            if index is not None and len(node.args) > index:
                arg = node.args[index]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip():
                    if not re.fullmatch(r"[{}\w\s%]*", arg.value) or " " in arg.value.strip():
                        found.add(arg.value)
    return found


def ui_texts() -> set[str]:
    texts = set()
    for template in (ROOT / "templates").glob("*.html"):
        texts |= {match.group(2) for match in TEMPLATE_CALL.finditer(template.read_text(encoding="utf-8"))}
    for source in [*(ROOT / "finder").glob("*.py"), ROOT / "app.py"]:
        texts |= _from_python(source)
    for question in QUESTIONS:
        texts |= {question["title"], *filter(None, [question.get("help")])}
        for field in question["fields"]:
            texts |= set(filter(None, [field.get("label"), field.get("help"), field.get("suffix")]))
            for _, label, sub in field.get("choices", []):
                texts |= set(filter(None, [label, sub]))
    texts |= {title for _, title in GROUPS}
    texts |= {"Type a question first.", "The helper has answered a lot of questions recently. Try again later."}
    from app import STATUS_LABELS, WHATS_NEW   # late import: app imports this package
    texts |= set(STATUS_LABELS.values()) | {str(line.template) for line in WHATS_NEW}
    for province in PROVINCE_FILES:
        benefits, links = load(province)
        texts |= {links["plan"][key] for key in ("rent_form_text", "tax_text") if links["plan"].get(key)}
        for benefit in benefits.values():
            texts |= {str(benefit["params"][key]).strip() for key in PARAM_TEXTS if key in benefit.get("params", {})}
    texts.discard("")
    # Templates that are only joins of other messages need no translation.
    return {text for text in texts if not re.fullmatch(r"(\{\w+\}\s*)+", text)}


def missing(lang: str) -> tuple[list[str], list[str]]:
    texts = catalog(lang).get("text", {})
    benefit_texts = catalog(lang).get("benefits", {})
    missing_ui = sorted(text for text in ui_texts() if text not in texts)
    missing_benefits = []
    for benefit_id, benefit in all_benefits().items():
        for field in ("name", "summary", "how_to_get", "also_called", "note"):
            if benefit.get(field) and not benefit_texts.get(benefit_id, {}).get(field):
                missing_benefits.append(f"{benefit_id}.{field}")
    return missing_ui, missing_benefits


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) > 1 else "fr"
    ui, benefits = missing(lang)
    print(f"{len(ui)} interface texts and {len(benefits)} benefit fields missing in {lang}")
    for text in ui:
        print("UI:", text)
    for key in benefits:
        print("BENEFIT:", key)
