exports.trackbar = (function() {
    var module = {};

    /**
     * The trackbar.
     *
     * @param parentEl
     *     The trackbar element.
     */
    var Trackbar = function(parentEl) {
        this.parentEl = parentEl;
    };
    module.Trackbar = Trackbar;

    return module;
})();

