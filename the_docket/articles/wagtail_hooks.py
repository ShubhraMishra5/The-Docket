from wagtail import hooks
from wagtail.admin.rich_text.editors.draftail import features as ft
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineStyleElementHandler, BlockElementHandler)


@hooks.register("register_rich_text_features")
def register_docket_features(features):
    # Underline -> <u>
    features.register_editor_plugin("draftail", "underline", ft.InlineStyleFeature(
        {"type": "UNDERLINE", "icon": "underline", "description": "Underline"}))
    features.register_converter_rule("contentstate", "underline", {
        "from_database_format": {"u": InlineStyleElementHandler("UNDERLINE")},
        "to_database_format": {"style_map": {"UNDERLINE": "u"}},
    })

    # Fonts -> <span class="font-...">
    fonts = [
        ("font-times", "TIMES", "Times", "Times New Roman, Times, serif"),
        ("font-sitka", "SITKA", "Sitka", "Sitka Small, Georgia, serif"),
        ("font-garamond", "GARAMOND", "Garamond", "Garamond, serif"),
    ]
    for name, ctype, label, css in fonts:
        features.register_editor_plugin("draftail", name, ft.InlineStyleFeature(
            {"type": ctype, "label": label, "description": label + " font",
             "style": {"fontFamily": css}}))
        features.register_converter_rule("contentstate", name, {
            "from_database_format": {f"span[class={name}]": InlineStyleElementHandler(ctype)},
            "to_database_format": {"style_map": {ctype: {"element": "span", "props": {"class": name}}}},
        })

    # Alignment -> <p class="align-...">
    for name, label in [("align-left", "Left"), ("align-center", "Center"), ("align-right", "Right")]:
        features.register_editor_plugin("draftail", name, ft.BlockFeature(
            {"type": name, "label": label, "description": "Align " + label.lower()}))
        features.register_converter_rule("contentstate", name, {
            "from_database_format": {f"p[class={name}]": BlockElementHandler(name)},
            "to_database_format": {"block_map": {name: {"element": "p", "props": {"class": name}}}},
        })
