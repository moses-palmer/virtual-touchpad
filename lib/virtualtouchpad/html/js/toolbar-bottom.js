exports.toolbar.bottom = (function() {
    var bottomToolbar, bottomToolbarEl;

    return {
        initialize: function(parentEl) {
            bottomToolbarEl = parentEl;
            bottomToolbar = new toolbar.Toolbar(bottomToolbarEl);

            // Hide the bottom toolbar after a while
            setTimeout(bottomToolbar.hide.bind(bottomToolbar), 2000);
        }};
})();

