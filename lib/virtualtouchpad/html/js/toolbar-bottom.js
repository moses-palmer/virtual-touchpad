exports.toolbar.bottom = (function() {
    var bottomToolbar, bottomToolbarEl;

    /**
     * Updates toolbar buttons to reflect the current fullscreen mode.
     */
    function fullscreenUpdate() {
        document.querySelector(".toolbar > .fullscreen-on").style.display =
            (document[document.FULLSCREEN_ELEMENT_NAME]
                    || checks.failed("Fullscreen"))
                ? "none"
                : "table-cell";
        document.querySelector(".toolbar > .fullscreen-off").style.display =
            (document[document.FULLSCREEN_ELEMENT_NAME]
                    && !checks.failed("Fullscreen"))
                ? "table-cell"
                : "none";
    }

    return {
        initialize: function(parentEl) {
            // Remove the toolbar element is SVGs are not supported
            if (checks.failed("SVG")) {
                parentEl.parentElement.removeChild(parentEl);
                return;
            }

            bottomToolbarEl = parentEl;
            bottomToolbar = new toolbar.Toolbar(bottomToolbarEl);

            // Hide the bottom toolbar after a while
            setTimeout(bottomToolbar.hide.bind(bottomToolbar), 2000);

            fullscreenUpdate();
            document.addEventListener(
                document.FULLSCREENCHANGE_EVENT_NAME,
                fullscreenUpdate);
        },

        onFullscreenOn: function() {
            document.documentElement.requestFullscreen();
        },

        onFullscreenOff: function() {
            document.exitFullscreen();
        }};
})();

