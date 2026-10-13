"""
Builds the monthly digest email content from ArticlePages published
(first_published_at) in a given month. Pure data/HTML building — no
Mailchimp calls here, so it's easy to test in isolation.
"""
import calendar
from datetime import date

from django.conf import settings
from django.utils.html import escape

from articles.models import ArticlePage


def month_bounds(year: int, month: int) -> tuple[date, date]:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def get_articles_for_month(year: int, month: int):
    start, end = month_bounds(year, month)
    return (
        ArticlePage.objects.live()
        .public()
        .filter(first_published_at__date__gte=start, first_published_at__date__lte=end)
        .order_by("path")
    )


def _absolute_url(page) -> str:
    base = getattr(settings, "PUBLIC_BASE_URL", "").rstrip("/")
    if base:
        return f"{base}{page.url}"
    try:
        return page.full_url
    except Exception:
        return page.url or ""


def build_monthly_digest(year: int, month: int):
    """Returns (subject, html_content, article_count). html_content is
    None if there's nothing published that month — caller should skip
    creating a campaign in that case."""
    articles = get_articles_for_month(year, month)
    count = articles.count()
    if count == 0:
        return None, None, 0

    month_name = calendar.month_name[month]
    subject = f"The Docket — {month_name} {year} Digest"

    # Group by practice area (the article's direct parent page)
    sections: dict[str, list] = {}
    for article in articles:
        section_title = article.get_parent().specific.title
        sections.setdefault(section_title, []).append(article)

    parts = [
        f"<h1 style='font-family:Georgia,serif;'>The Docket — {month_name} {year}</h1>",
        "<p>This month's pieces:</p>",
    ]
    for section_title, section_articles in sections.items():
        parts.append(
            f"<h2 style='font-family:Georgia,serif;font-size:18px;'>{escape(section_title)}</h2>"
        )
        for article in section_articles:
            parts.append(
                "<div style='margin-bottom:16px;'>"
                f"<a href='{_absolute_url(article)}' style='font-size:16px;font-weight:bold;color:#24558a;'>{escape(article.title)}</a>"
                f"<p style='margin:4px 0;color:#444;'>{escape(article.intro)}</p>"
                "</div>"
            )

    parts.append(
        "<hr style='margin-top:32px;border:none;border-top:1px solid #ddd;'>"
        "<p style='font-size:12px;color:#777;'>"
        "You're receiving this because you subscribed to The Docket. "
        "<a href='*|UNSUB|*'>Unsubscribe</a></p>"
        "<p style='font-size:12px;color:#777;'>*|HTML:LIST_ADDRESS_HTML|*</p>"
    )

    html_content = "\n".join(parts)
    return subject, html_content, count
