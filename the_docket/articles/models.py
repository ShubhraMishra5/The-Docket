from django import forms
from django.db import models
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index


# --- The four content types every section offers, per the brief ---
CONTENT_TYPE_CHOICES = [
    ("blog", "Blog"),
    ("case_commentary", "Case Commentary"),
    ("policy_regulatory", "Policy and Regulatory Updates"),
    ("cross_border", "Cross-border Insights"),
]


class SectionIndexPage(Page):
    """
    One of these per practice area: Investment Funds, Capital Markets,
    Foreign Investment, Taxation. Holds ArticlePage children and powers
    the per-section search.
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    subpage_types = ["articles.ArticlePage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        context = super().get_context(request)

        articles = ArticlePage.objects.live().public().descendant_of(self).order_by(
            "-date"
        )

        piece_type = request.GET.get("type")
        if piece_type:
            articles = articles.filter(piece_type=piece_type)

        query = request.GET.get("q")
        if query:
            # .search() returns a SearchResults object, so it must be
            # the last step.
            articles = articles.search(query)

        context["articles"] = articles
        context["content_types"] = CONTENT_TYPE_CHOICES
        context["active_type"] = piece_type
        context["search_query"] = query or ""

        return context


class ArticlePage(Page):
    """
    A single piece: blog post, case commentary, policy update, or
    cross-border insight, inside one of the four practice areas.
    """

    piece_type = models.CharField(
        max_length=32,
        choices=CONTENT_TYPE_CHOICES,
        default="blog",
    )

    author = models.CharField(
        max_length=120,
        default="Tvisha Zatakia",
    )

    date = models.DateField("Publication date")

    intro = models.CharField(
        max_length=300,
        help_text="Short summary shown on cards and in search results.",
    )

    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # The actual piece. Editors can mix formatted text, images,
    # embedded video, and attached PDFs/documents in any order.
    body = StreamField(
        [
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=[
                        "bold",
                        "italic",
                        "underline",
                        "ol",
                        "ul",
                        "link",
                        "align-left",
                        "align-center",
                        "align-right",
                    ]
                ),
            ),
            ("image", ImageChooserBlock()),
            ("document", DocumentChooserBlock()),
            (
                "embed",
                EmbedBlock(
                    help_text="Paste a YouTube/Vimeo link to embed video."
                ),
            ),
        ],
        use_json_field=True,
    )

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
        index.FilterField("piece_type"),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("piece_type", widget=forms.RadioSelect),
        FieldPanel("author"),
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("cover_image"),
        FieldPanel("body"),
    ]

    parent_page_types = ["articles.SectionIndexPage"]
    subpage_types = []

    class Meta:
        ordering = ["-date"]


class AboutAuthorPage(Page):
    bio = RichTextField()

    linkedin_url = models.URLField(
        default="https://www.linkedin.com/company/the-docket/"
    )

    phone = models.CharField(
        max_length=30,
        default="+91 8153839771",
    )

    email = models.EmailField(
        default="thedocketrepository@outlook.com"
    )

    content_panels = Page.content_panels + [
        FieldPanel("bio"),
        FieldPanel("linkedin_url"),
        FieldPanel("phone"),
        FieldPanel("email"),
    ]

    parent_page_types = ["home.HomePage"]
    max_count = 1


class SpecialIssuePage(Page):
    body = RichTextField(
        help_text=(
            "Updates about the Special Issue are announced on LinkedIn; "
            "use this page to point readers there."
        )
    )

    linkedin_url = models.URLField(
        default="https://www.linkedin.com/company/the-docket/"
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("linkedin_url"),
    ]

    parent_page_types = ["home.HomePage"]
    max_count = 1