exports.toolbar = (function() {
    var module = {};

    /**
     * The toolbar.
     */
    var Toolbar = function(parentEl) {
        this.parentEl = parentEl;

        this.parentEl.addEventListener("touchstart",
            this.onTouchStart.bind(this));
        this.parentEl.addEventListener("touchend",
            this.onTouchEnd.bind(this));
        this.parentEl.addEventListener("touchcancel",
            this.onTouchCancel.bind(this));
        this.parentEl.addEventListener("touchleave",
            this.onTouchEnd.bind(this));
        this.parentEl.addEventListener("touchmove",
            this.onTouchMove.bind(this));

        this.applyClass();
    };
    module.Toolbar = Toolbar;

    /**
     * Applies styles necessary fo this type of toolbar class.
     */
    Toolbar.prototype.applyClass = function() {
        if (this.parentEl.classList.contains("bottom")) {
            // TODO: Implement
        }

        else {
            throw "Unknown tool bar type";
        }
    };

    Toolbar.prototype.onTouchStart = function(event) {
        // TODO: Implement
    };

    Toolbar.prototype.onTouchEnd = function(event) {
        // TODO: Implement
    };

    Toolbar.prototype.onTouchCancel = function(event) {
        // TODO: Implement
    };

    Toolbar.prototype.onTouchLeave = function(event) {
        // TODO: Implement
    };

    Toolbar.prototype.onTouchMove = function(event) {
        // TODO: Implement
    };

    return module;
})();

