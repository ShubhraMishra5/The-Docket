"""
Creates (or refreshes) the monthly digest as a DRAFT campaign in Mailchimp.
Never sends anything — sending is a manual step in Mailchimp's dashboard.

Usage:
    python manage.py create_monthly_digest
        → targets last calendar month (what you'd run via cron on the 1st)

    python manage.py create_monthly_digest --year 2026 --month 9
        → target a specific month, for testing
"""
from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand, CommandError

from articles.digest import build_monthly_digest
from subscribers.mailchimp import create_or_update_monthly_draft


class Command(BaseCommand):
    help = "Create or update this month's digest as a Mailchimp draft campaign."

    def add_arguments(self, parser):
        parser.add_argument("--year", type=int, default=None)
        parser.add_argument("--month", type=int, default=None)

    def handle(self, *args, **options):
        if options["year"] and options["month"]:
            year, month = options["year"], options["month"]
        else:
            target = date.today() - relativedelta(months=1)
            year, month = target.year, target.month

        subject, html_content, count = build_monthly_digest(year, month)

        if count == 0:
            self.stdout.write(self.style.WARNING(
                f"No articles published in {month}/{year} — nothing created."
            ))
            return

        campaign_title = f"The Docket — Monthly Digest — {year}-{month:02d}"
        result = create_or_update_monthly_draft(
            title=campaign_title, subject=subject, html_content=html_content
        )

        if result == "created":
            self.stdout.write(self.style.SUCCESS(
                f"created: draft '{campaign_title}' with {count} article(s). Review it in Mailchimp."
            ))
        elif result == "updated":
            self.stdout.write(self.style.SUCCESS(
                f"updated: existing draft '{campaign_title}' with {count} article(s)."
            ))
        elif result == "skipped_already_sent":
            self.stdout.write(self.style.WARNING(
                f"skipped_already_sent: '{campaign_title}' was already sent/queued — left untouched."
            ))
        else:
            self.stdout.write(self.style.ERROR(f"failed: could not create/update '{campaign_title}'."))
            raise CommandError(f"Could not create/update Mailchimp campaign '{campaign_title}'.")
