# Putting the Benefits Finder online

The site is a small Flask app with no database. Anything that runs Python 3.11+ can host it.

## Before you start: pick where it lives

CalcLearners already uses PythonAnywhere. A free PythonAnywhere account allows **one** web app,
so the Benefits Finder needs one of these:

| Option | Cost | Notes |
|---|---|---|
| Upgrade PythonAnywhere to a paid plan with room for a second web app | Monthly fee (check their pricing page) | Same steps you already know from CalcLearners. Custom domain supported. |
| A second free PythonAnywhere account | Free | Address is `yourname.pythonanywhere.com`; no custom domain on free. |
| Another host (Render, Fly.io, or a small VPS) | Free tier to a few dollars | Run `gunicorn wsgi:application`. |

This is your call (it may cost money), so nothing has been set up yet.

## PythonAnywhere steps

1. The code is on GitHub: https://github.com/ZohaibKhawar/benefits-finder
2. On PythonAnywhere, open a **Bash console** and clone it:
   ```
   git clone https://github.com/ZohaibKhawar/benefits-finder.git benefits-finder
   cd benefits-finder
   pip install --user -r requirements.txt
   python -m pytest
   ```
3. **Web tab, Add a new web app**, Manual configuration, Python 3.11 (or newer).
4. **Source code:** `/home/<you>/benefits-finder`.
5. **WSGI file:** replace its contents with:
   ```python
   import sys
   sys.path.insert(0, "/home/<you>/benefits-finder")
   from wsgi import application
   ```
6. **Static files:** URL `/static/`, directory `/home/<you>/benefits-finder/static`.
7. **Environment variables** (put them at the top of the WSGI file with `os.environ[...] = ...`, or in
   a `.env` you load there):
   - `SITE_URL` = the public address, e.g. `https://benefitsfinder.example` (used in the sitemap and
     search-engine tags).
   - `CONTACT_EMAIL` = **required before going live.** An address people can write to about privacy or
     a mistake. It shows on the privacy page and as "Report a mistake" in the footer. Use a separate
     address, not your personal one.
   - `ANTHROPIC_API_KEY` = only if you want the "Ask about your results" helper. Leave it out and the
     helper doesn't appear at all. You type the key in yourself; never commit it.
   - `BENEFITS_AI_DAILY_LIMIT` = optional cap on helper questions per day (default 500). At Claude
     Haiku 5.5 prices that is well under $1 a day even if every slot is used.
8. **Force HTTPS** on the Web tab, then **Reload**.
9. **Updating later:** in the console, `git pull`, run `python -m pytest`, then press **Reload**.

## After it's live

- Google Search Console: add the site, verify with the HTML tag (same as CalcLearners), and submit
  `https://<your site>/sitemap.xml`.
- The GitHub workflow in `.github/workflows/` runs the tests on every push and the link check every Monday.
- Follow `UPDATING.md` every January and July.
