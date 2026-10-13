(function () {
    function makeControl(type, letter, title) {
        return function FontControl(props) {
            var isActive =
                props.selection &&
                props.selection.getCurrentInlineStyle
                    ? props.selection.getCurrentInlineStyle().has(type)
                    : false;

            return window.React.createElement(
                "button",
                {
                    type: "button",
                    className:
                        "Draftail-ToolbarButton" +
                        (isActive ? " Draftail-ToolbarButton--active" : ""),
                    title: title,
                    onMouseDown: function (e) {
                        e.preventDefault();
                        props.onToggle(type);
                    },
                },
                letter
            );
        };
    }

    if (!window.draftail || !window.React) {
        return;
    }

    window.draftail.registerPlugin(
        {
            type: "TIMES",
            source: makeControl("TIMES", "T", "Times New Roman"),
        },
        "inlineStyles"
    );

    window.draftail.registerPlugin(
        {
            type: "SITKA",
            source: makeControl("SITKA", "S", "Sitka Small"),
        },
        "inlineStyles"
    );

    window.draftail.registerPlugin(
        {
            type: "GARAMOND",
            source: makeControl("GARAMOND", "G", "Garamond"),
        },
        "inlineStyles"
    );
})();