exports.toolbar.bottom = (function() {
    var bottomToolbar, bottomToolbarEl;

    return {
        initialize: function(parentEl) {
            bottomToolbarEl = parentEl;
            bottomToolbar = new toolbar.Toolbar(bottomToolbarEl);
        }};
})();

