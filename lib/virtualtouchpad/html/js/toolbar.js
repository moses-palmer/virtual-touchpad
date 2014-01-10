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

            // The value of bottom when the hide animation is started
            var hiddenInitialBottom,

            // The difference between the current bottom and the desired bottom
            // when hideStart is called
                hiddenInitialDiff,

            // The value to which to reset bottom when hiding
                hiddenBottom = -(4 * this.parentEl.clientHeight / 5);

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

                this._locked = bottom >= 0;
            };

            this.hideStart = function() {
                hiddenInitialBottom = this.parentElBottom();
                hiddenInitialDiff = hiddenBottom - hiddenInitialBottom;
            };

            this.hideUpdate = function() {
                var currentDiff = hiddenBottom - this.parentElBottom();

                    progress = 1 - currentDiff / hiddenInitialDiff,

                    // The relative progress; we add a small value to move
                    t = Math.sin(Math.PI * 0.5 * (progress + 0.1));

                // Cap t
                if (t > 1.0) {
                    t = 1.0;
                }
                else if (t < 0.0) {
                    t = 0.0;
                }

                // Set the bottom; make sure to use px
                this.parentEl.style.bottom = (
                    hiddenInitialBottom + hiddenInitialDiff * t)
                        .toFixed(0) + "px";

                return this.parentElBottom() == hiddenBottom;
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

    /**
     * Starts the hide animation.
     *
     * The hiding may be cancelled by calling hideCancel until it has completed.
     */
    Toolbar.prototype.hide = function() {
        // Do nothing if already hiding
        if (this._hideInterval) {
            return;
        }

        // Notify about start of animation
        this.hideStart();

        // Then update until completed
        this._hideInterval = setInterval(
            (function() {
                // Stop hiding if we are finished
                if (this.hideUpdate() === true) {
                    this.hideStop();
                }
            }).bind(this),
            50);
    };

    /**
     * Stops the current hide animation.
     *
     * @return whether the animation was stopped
     */
    Toolbar.prototype.hideStop = function() {
        if (this._hideInterval) {
            clearInterval(this._hideInterval);
            this._hideInterval = undefined;
            return true;
        }
        else {
            return false;
        }
    };

    Toolbar.prototype.onTouchStart = function(event) {
        this._identifier = event.touches[0].identifier;
        this.start(event);

        // Clear any timers that might interfere
        this.hideStop();
        if (this._hideTimer) {
            clearTimeout(this._hideTimer);
            this._hideTimer = undefined;
        }
    };

    Toolbar.prototype.onTouchEnd = function(event) {
        if (!this._locked) {
            this.hide();
        }
        else {
            this._hideTimer = setTimeout(
                (function() {
                    this.hide();
                }).bind(this),
                3000);
        }
    };

    Toolbar.prototype.onTouchCancel = function(event) {
        this.hide();
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

