exports.toolbar.bottom = (function() {
    var bottomToolbar, bottomToolbarEl;

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
        },

        onFullscreenOn: function() {
            document.documentElement.requestFullscreen();
        },

        onFullscreenOff: function() {
            document.exitFullscreen();
        }};
})();

