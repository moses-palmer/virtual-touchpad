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
     *
     * This function also sets up methods to handle touch events.
     */
    Toolbar.prototype.applyClass = function() {
        if (this.parentEl.classList.contains("bottom")) {
            // Initial values set on start
            var initialX,
                initialY,
                initialBottom;

            this.start = function(event) {
                initialX = event.touches[0].screenX;
                initialY = event.touches[0].screenY;
                initialBottom = this.parentElBottom();
            };

            this.setPosition = function(touch) {
                var dy = initialY - touch.screenY;
                var bottom = initialBottom + dy;

                this.parentEl.style.bottom = (bottom > 0
                    ? 0
                    : bottom > -this.parentEl.clientHeight
                        ? bottom
                        : -this.parentEl.clientHeight) + "px";
            };
        }

        else {
            throw "Unknown tool bar type";
        }
    };

    /**
     * Returns the current value of the bottom of the parent element in px.
     */
    Toolbar.prototype.parentElBottom = function() {
        // TODO: Do not assume bottom is in px
        var result = parseInt(getComputedStyle(this.parentEl)
            .getPropertyValue("bottom"));
        return isNaN(result)
            ? 0
            : result;
    }

    Toolbar.prototype.onTouchStart = function(event) {
        this._identifier = event.touches[0].identifier;
        this.start(event);
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
        var touch = event.changedTouches.identifiedTouch(this._identifier);
        if (touch) {
            this.setPosition(touch);
        }

        event.preventDefault();
    };

    return module;
})();

