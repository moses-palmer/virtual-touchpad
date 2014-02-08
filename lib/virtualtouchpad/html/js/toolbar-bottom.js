exports.toolbar.bottom = (function() {
    /**
     * Updates toolbar buttons to reflect the current fullscreen mode.
     */
    function fullscreenUpdate() {
        document.querySelector("toolbar > .fullscreen-on").style.display =
            (document[document.FULLSCREEN_ELEMENT_NAME]
                    || checks.failed("Fullscreen"))
                ? "none"
                : "table-cell";
        document.querySelector("toolbar > .fullscreen-off").style.display =
            (document[document.FULLSCREEN_ELEMENT_NAME]
                    && !checks.failed("Fullscreen"))
                ? "table-cell"
                : "none";
    }

    /**
     * Remove the bottom toolbar if SVGs are not supported, otherwise update the
     * fullscreen buttons.
     */
    exports.onloadCallbacks.push(function() {
        var bottomToolbar = toolbar.find("#toolbar-bottom")[0];

        // Remove the toolbar element if SVGs are not supported
        if (checks.failed("SVG")) {
            bottomToolbar.parentEl.parentElement.removeChild(
                bottomToolbar.parentEl);
            return;
        }

        fullscreenUpdate();
        document.addEventListener(
            document.FULLSCREENCHANGE_EVENT_NAME,
            fullscreenUpdate);
    });

    return {
        onHelp: function() {
            if (document.location.pathname.indexOf(".min.xhtml") != -1) {
                window.open("help.min.xhtml", "_blank");
            }
            else {
                window.open("help.xhtml", "_blank");
            }
        },

        onFullscreenOn: function() {
            document.documentElement.requestFullscreen();
        },

        onFullscreenOff: function() {
            document.exitFullscreen();
        }};
})();

