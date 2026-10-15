from django.core.management.base import BaseCommand

from subscribers.mailchimp import add_subscriber
from subscribers.models import Subscriber


class Command(BaseCommand):
    help = "Add every not-yet-synced subscriber to the Mailchimp Audience."

    def handle(self, *args, **options):
        done = failed = 0
        for sub in Subscriber.objects.filter(synced_to_mailchimp=False):
            if add_subscriber(sub.email):
                sub.synced_to_mailchimp = True
                sub.save(update_fields=["synced_to_mailchimp"])
                done += 1
            else:
                failed += 1
        self.stdout.write(f"Synced {done}, failed {failed}.")