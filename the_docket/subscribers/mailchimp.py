"""
Mailchimp integration for The Docket.

1. add_subscriber(email)            -> adds/updates a contact in your Audience
2. handle_new_subscriber(email)     -> add to Audience + thank-you email to the
                                       subscriber + notification to the owner
3. create_or_update_monthly_draft() -> creates (or refreshes) a DRAFT campaign
                                       for Tvisha to review and send herself

SAFETY: nothing here can send a campaign. Mailchimp's send/schedule endpoints
(/actions/send, /actions/schedule) are deliberately never called.

Thank-you / owner emails use Django's normal email system (EMAIL_* in
settings.py), because Mailchimp's transactional email is a separate paid product.
"""
import hashlib
import logging

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)
TIMEOUT = 20


# ---------- helpers ----------

def _base_url():
    """API key looks like 'abc123...-us21'; the part after '-' is the data centre."""
    key = settings.MAILCHIMP_API_KEY
    if not key or "-" not in key:
        return None
    return f"https://{key.rsplit('-', 1)[1]}.api.mailchimp.com/3.0"


def _request(method, path, **kwargs):
    base = _base_url()
    if not base:
        raise RuntimeError("MAILCHIMP_API_KEY is missing or invalid (should end like -us21)")
    return requests.request(
        method, base + path,
        auth=("anystring", settings.MAILCHIMP_API_KEY),
        timeout=TIMEOUT, **kwargs,
    )


# ---------- subscribers ----------

def add_subscriber(email):
    """Add the email to the Audience. Safe to call twice for the same address."""
    email = email.strip().lower()
    member_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
    try:
        resp = _request(
            "PUT",
            f"/lists/{settings.MAILCHIMP_AUDIENCE_ID}/members/{member_hash}",
            json={"email_address": email, "status_if_new": "subscribed"},
        )
    except Exception:
        logger.exception("Mailchimp add_subscriber failed for %s", email)
        return False
    if resp.status_code not in (200, 201):
        logger.error("Mailchimp add_subscriber %s: %s", resp.status_code, resp.text[:300])
        return False
    return True


def _safe_mail(subject, message, to):
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=False)
        return True
    except Exception:
        logger.exception("Could not send email to %s", to)
        return False


def handle_new_subscriber(email):
    """Called by the subscribe form. Never raises, so the form never crashes."""
    added = add_subscriber(email)
    _safe_mail(
        "Welcome to The Docket",
        "Thank you for subscribing to The Docket.\n\n"
        "You will receive a monthly note when new pieces are published.\n\n"
        "— The Docket",
        email,
    )
    owner = settings.OWNER_NOTIFICATION_EMAIL
    if owner:
        _safe_mail("New Docket subscriber", f"{email} subscribed to The Docket.", owner)
    return added


# ---------- monthly draft campaign ----------

def find_campaign_by_title(title):
    """Return {'id':..., 'status':...} for a campaign with exactly this title, or None."""
    resp = _request(
        "GET", "/campaigns",
        params={"count": 100, "sort_field": "create_time", "sort_dir": "DESC",
                "fields": "campaigns.id,campaigns.status,campaigns.settings.title"},
    )
    if resp.status_code != 200:
        logger.error("Mailchimp list campaigns %s: %s", resp.status_code, resp.text[:300])
        raise RuntimeError(f"list campaigns failed: {resp.status_code}")
    for c in resp.json().get("campaigns", []):
        if c.get("settings", {}).get("title") == title:
            return {"id": c["id"], "status": c["status"]}
    return None


def _settings(title, subject):
    return {
        "title": title,
        "subject_line": subject,
        "from_name": "The Docket",
        "reply_to": settings.MAILCHIMP_REPLY_TO,
    }


def _set_content(campaign_id, html):
    resp = _request("PUT", f"/campaigns/{campaign_id}/content", json={"html": html})
    if resp.status_code != 200:
        raise RuntimeError(f"set content failed: {resp.status_code} {resp.text[:300]}")


def create_or_update_monthly_draft(title, subject, html_content):
    """
    Returns 'created' | 'updated' | 'skipped_already_sent' | 'failed'.
    Mailchimp calls a draft status 'save'. Anything else (sent, scheduled,
    sending, paused) is left completely alone.
    """
    try:
        existing = find_campaign_by_title(title)
        if existing:
            if existing["status"] != "save":
                return "skipped_already_sent"
            r = _request("PATCH", f"/campaigns/{existing['id']}",
                         json={"settings": _settings(title, subject)})
            if r.status_code != 200:
                raise RuntimeError(f"update failed: {r.status_code} {r.text[:300]}")
            _set_content(existing["id"], html_content)
            return "updated"

        r = _request("POST", "/campaigns", json={
            "type": "regular",
            "recipients": {"list_id": settings.MAILCHIMP_AUDIENCE_ID},
            "settings": _settings(title, subject),
        })
        if r.status_code != 200:
            raise RuntimeError(f"create failed: {r.status_code} {r.text[:300]}")
        _set_content(r.json()["id"], html_content)
        return "created"
    except Exception:
        logger.exception("Mailchimp draft failed")
        return "failed"