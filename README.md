# Claimable

The site's public name is **Claimable**. It was called Benefits Finder until 2026-10-19, but that is the
name of the Government of Canada's own tool, so it was renamed; the repository and folder keep the old name.

A free website that asks students and newcomers in Canada 13 short questions and lists the credits and
benefits they might qualify for, with a rough amount, what to do first, and the official link for each.
All ten provinces and the three territories, English and French. Nothing is saved.

Status (2026-10-18): built and tested, not online yet. See [ROADMAP.md](ROADMAP.md).

This is a guide, not tax, legal or immigration advice, and it isn't affiliated with any government.
Every result links to the official page, which has the final word.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5240 (French at /fr/).

```bash
python -m pytest
python check_links.py
python -m finder.demo
python -m finder.i18n_keys fr
```

The tests (172) check the formulas against official numbers. `check_links.py` opens every official
link. `finder.demo` prints results for five sample people. `finder.i18n_keys fr` lists anything
without a French translation.

## Where things are

| Path | What |
|---|---|
| `app.py`, `wsgi.py` | The website (Flask) and the entry point for hosting |
| `finder/answers.py` | What a person told us |
| `finder/form.py` | The 13 questions and turning a form into answers |
| `finder/rules.py` | Who qualifies for what (likely / maybe / not yet / no), one rule per benefit or shared rule |
| `finder/estimates.py` | Dollar formulas from the official sources |
| `finder/engine.py` | Runs the rules, totals the money, builds the step-by-step plan |
| `finder/i18n.py`, `translations/fr.yaml` | English and French |
| `finder/calendar.py` | The calendar download |
| `finder/ask.py` | Optional AI helper (Claude Haiku 5.5), off without `ANTHROPIC_API_KEY` |
| `data/*.yaml` | Every benefit: text, numbers, official link, last checked |
| `templates/`, `static/` | Pages, styles, the questionnaire script |
| `tests/` | Formulas, rules, sample people, provinces, website, French, accessibility, AI helper |
| `research/` | Sources for every number |
| `DEPLOY.md`, `UPDATING.md` | Putting it online, keeping the numbers current |

## Research

- [01 federal benefits](research/01-federal-benefits.md)
- [02 Ontario](research/02-ontario-benefits.md)
- [03 newcomers and students](research/03-newcomers-and-students.md)
- [04 existing tools, legal, privacy, accessibility](research/04-existing-tools-legal-privacy.md)
- [05 other provinces, the territories and Ontario cities](research/05-other-provinces.md)

## License

MIT. See [LICENSE](LICENSE). Corrections to numbers are welcome: open an issue with the official page that shows the right value.
