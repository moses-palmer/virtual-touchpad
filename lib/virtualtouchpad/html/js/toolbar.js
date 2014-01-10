exports.toolbar = (function() {
    var module = {};

    /**
     * The toolbar.
     */
    var Toolbar = function(parentEl) {
        this.parentEl = parentEl;
    };
    module.Toolbar = Toolbar;

    return module;
})();

