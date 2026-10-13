from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page

from articles.models import ArticlePage


class HomePage(Page):
    """The landing page. Only one of these should exist (the site root)."""

    eyebrow = models.CharField(
        max_length=120, default="An editorial repository from India"
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_heading = models.CharField(max_length=255, blank=True)
    hero_intro = RichTextField(blank=True)

    premise_heading = models.CharField(max_length=120, default="The premise")
    premise_body = RichTextField(blank=True)

    offer_heading = models.CharField(
        max_length=255,
        default="These topics were never meant to be read in isolation.",
    )
    offer_body = RichTextField(blank=True)

    newsletter_heading = models.CharField(
        max_length=120, default="Keep the record close."
    )
    newsletter_body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("eyebrow"),
        FieldPanel("hero_image"),
        FieldPanel("hero_heading"),
        FieldPanel("hero_intro"),
        FieldPanel("premise_heading"),
        FieldPanel("premise_body"),
        FieldPanel("offer_heading"),
        FieldPanel("offer_body"),
        FieldPanel("newsletter_heading"),
        FieldPanel("newsletter_body"),
    ]

    # Only one HomePage should exist; nothing besides section indexes,
    # the About Author page, and the Special Issue page live under it.
    subpage_types = [
        "articles.SectionIndexPage",
        "articles.AboutAuthorPage",
        "articles.SpecialIssuePage",
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["recent_pieces"] = (
            ArticlePage.objects.live().public().order_by("-date")[:3]
        )
        return context