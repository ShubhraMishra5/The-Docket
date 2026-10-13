# The Docket — Wagtail site

A Wagtail/Django CMS for The Docket, built to match `Docket_Details.docx`:
four practice areas (Investment Funds, Capital Markets, Foreign Investment,
Taxation), each with Blog / Case Commentary / Policy and Regulatory Updates /
Cross-border Insights; About Author; Special Issue; per-section search;
rich-text formatting with font choice, image/video/PDF embedding; and a
subscribe flow wired to Brevo for the thank-you email, owner notification,
and monthly digest.

**This was written without network access, so it has not been run.** The
code is complete and internally consistent (imports, model relationships,
and URL wiring were checked by hand), but you'll hit the normal first-run
issues any new Django project has. Follow the steps below in order.

## 1. Local setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`: set `DJANGO_SECRET_KEY` to any long random string. Leave
`DATABASE_URL` blank for now — it'll use a local SQLite file.

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # this becomes Tvisha's admin login
python manage.py runserver
```

Visit `http://localhost:8000/admin/` and log in — that's the Wagtail CMS.

## 2. Build the page tree (one-time, in the Wagtail admin)

Wagtail starts with a blank "Welcome to Wagtail" root page. Replace it:

1. In the admin, go to **Pages**, delete the default "Welcome to Wagtail" page it starts with, keep the Root.
2. Under Root, **Add child page → Home Page**. Fill in the hero/premise/offer/newsletter text from the brief. Publish it.
3. **Set it as the site root**: Settings → Sites → edit the default site → set Root page to your new Home Page.
4. Under Home Page, add four **Section Index Page** children: "Investment Funds", "Capital Markets", "Foreign Investment", "Taxation".
5. Under Home Page, add one **About Author Page** and one **Special Issue Page**, using the bio/contact text from the brief.
6. Under each Section Index Page, add **Article Page** children as pieces get written — each one picks its type (Blog / Case Commentary / Policy and Regulatory Updates / Cross-border Insights), a date, a short intro, and a body where you mix formatted text, images, embedded video, and PDF attachments freely.

## 3. The rich-text font toolbar — please test this one

`articles/wagtail_hooks.py` + `static/js/font-features.js` add Times New
Roman / Sitka Small / Garamond buttons to the editor toolbar, so a
selection can be set to any of those fonts (the brief's formatting
requirement). Draftail's plugin API has changed across Wagtail versions,
so **check that these three buttons actually appear and toggle correctly**
after your first `runserver`. If they don't, Wagtail's own docs page,
"Extending the Draftail Editor," has the current API for your installed
version — the fix is usually a small adjustment to `font-features.js`,
not a rewrite.

## 4. Brevo (subscriber list + emails)

1. Create a free account at brevo.com.
2. Settings → SMTP & API → API Keys → generate a key → put it in `.env` as `BREVO_API_KEY`.
3. Contacts → Lists → create a list (e.g. "The Docket subscribers") → the number in its URL is `BREVO_LIST_ID`.
4. That's it for signup — `subscribers/brevo.py` handles adding contacts and sending the thank-you + owner-notification emails automatically.

**Monthly digest:** this is intentionally manual, not scheduled, per your
"minimal interference" priority — no cron job to babysit. When you publish
that month's piece, go to Brevo → Campaigns → create a campaign to your
list linking the new piece, and send it. Takes two minutes, and Brevo
handles unsubscribe links and deliverability for you.

## 5. Deploying to Render

Netlify can't run this (it's a static host; this is a Python/Postgres app).

1. Push this project to a GitHub repo.
2. On Render: **New → Web Service**, connect the repo.
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn docket.wsgi:application`
3. **New → PostgreSQL**, create a database. Copy its "Internal Database URL" into the web service's `DATABASE_URL` environment variable.
4. Set the same environment variables from `.env` on the Render service (`DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` — your `*.onrender.com` domain, `BREVO_API_KEY`, `BREVO_LIST_ID`, etc). Set `DJANGO_DEBUG=False`.
5. Deploy. Then run `python manage.py createsuperuser` once via Render's shell tab to create Tvisha's login on the live site.

## What's left to layer on

- The exact dark-blue hex codes from the Wix reference (I used a formal
  navy/white palette derived from your existing prototype — swap the
  `--accent`/`--deep` variables in `static/css/docket.css` if you get the
  real ones).
- Populating actual content (the page tree above is empty until you add pieces).
- Any visual polish once you see it rendered — I built this blind, without a browser to check it in.
