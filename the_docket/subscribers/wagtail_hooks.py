from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Subscriber


class SubscriberViewSet(SnippetViewSet):
    model = Subscriber
    icon = "group"
    menu_label = "Subscribers"
    menu_order = 300
    add_to_admin_menu = True
    list_display = ["email", "subscribed_at", "synced_to_mailchimp"]
    list_filter = ["synced_to_mailchimp"]
    search_fields = ["email"]
    list_export = ["email", "subscribed_at", "synced_to_mailchimp"]


register_snippet(SubscriberViewSet)