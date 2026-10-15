from django.db import models


class Subscriber(models.Model):
    """Local backup of everyone who used the subscribe form."""
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    synced_to_mailchimp = models.BooleanField(
        default=False,
        help_text="Ticked once this address has been added to the Mailchimp Audience.",
    )

    class Meta:
        ordering = ["-subscribed_at"]

    def __str__(self):
        return self.email