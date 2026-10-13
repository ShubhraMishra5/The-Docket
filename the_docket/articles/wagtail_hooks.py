from django.templatetags.static import static
from django.utils.html import format_html

from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler,
)
from wagtail.admin.rich_text.editors.draftail import features as draftail_features


FONT_FEATURES = [
    ("font-times", "TIMES", "Times New Roman", "T"),
    ("font-sitka", "SITKA", "Sitka Small", "S"),
    ("font-garamond", "GARAMOND", "Garamond", "G"),
]


@hooks.register("insert_editor_js")
def font_features_js():
    return format_html(
        '<script src="{}"></script>',
        static("js/font-features.js"),
    )


@hooks.register("register_rich_text_features")
def register_font_features(features):
    for feature_name, type_, font_family, label in FONT_FEATURES:
        features.register_editor_plugin(
            "draftail",
            feature_name,
            draftail_features.InlineStyleFeature(
                {
                    "type": type_,
                    "label": label,
                    "description": font_family,
                    "style": {
                        "fontFamily": font_family,
                    },
                }
            ),
        )

        features.register_converter_rule(
            "contentstate",
            feature_name,
            {
                "from_database_format": {
                    f"span[class={feature_name}]": InlineStyleElementHandler(type_)
                },
                "to_database_format": {
                    "style_map": {
                        type_: {
                            "element": "span",
                            "props": {"class": feature_name},
                        }
                    }
                },
            },
        )

        features.default_features.append(feature_name)