exports.view = (function() {
    var module = {};

    /**
     * The touchpad view.
     *
     * @param parentEl
     *     The touchpad view element.
     * @param touchpad
     *     The controller to use.
     */
    var Touchview = function(parentEl, touchpad) {
        this.parentEl = parentEl;
        this.touchpad = touchpad;

        var self = this;
        var touchstart, touchend, touchcancel, touchleave, touchmove;
        this.parentEl.addEventListener("touchstart", touchstart = function() {
            return self.onTouchStart.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchend", touchend = function() {
            return self.onTouchEnd.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchcancel", touchcancel = function() {
            return self.onTouchCancel.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchleave", touchleave = function() {
            return self.onTouchEnd.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchmove", touchmove = function() {
            return self.onTouchMove.apply(self, arguments);
        });

        this.detach = function() {
            this.parentEl.removeEventListener("touchstart", touchstart);
            this.parentEl.removeEventListener("touchend", touchend);
            this.parentEl.removeEventListener("touchcancel", touchcancel);
            this.parentEl.removeEventListener("touchleave", touchleave);
            this.parentEl.removeEventListener("touchmove", touchmove);
        };
    };
    module.Touchview = Touchview;

    /**
     * Calculates the movement vector given the old and new touch events.
     *
     * @param oldTouch, newTouch
     *     The previous and current touch events.
     * @return the movement vector [dx, dy]
     */
    function calculateMovement(oldTouch, newTouch) {
        var dx = newTouch.screenX - oldTouch.screenX;
        var dy = newTouch.screenY - oldTouch.screenY;
        var d = Math.sqrt(dx * dx + dy * dy);
        var a = Math.atan2(dy, dx);

        var acceleration = configuration.get("view.acceleration", 0.3);
        var sensitivity = configuration.get("view.sensitivity", 1.5);

        var h = sensitivity * Math.pow(d, 1.0 + acceleration);

        return [Math.cos(a) * h, Math.sin(a) * h];
    }

    /**
     * Calculates the scroll vector given the old and new touch events.
     *
     * @param oldTouch, newTouch
     *     The previous and current touch events.
     * @return the scroll vector [dx, dy]
     */
    function calculateScroll(oldTouch, newTouch) {
        var dx = newTouch.screenX - oldTouch.screenX;
        var dy = newTouch.screenY - oldTouch.screenY;

        var xdirection = configuration.get("view.naturalScroll", true)
            ? -1
            : 1;
        var ydirection = configuration.get("view.naturalScroll", true)
            ? -1
            : 1;

        return [dx * xdirection, dy * ydirection];
    }

    /**
     * Clicks a button.
     *
     * The click will be sent with a short delay. Before the click is actually
     * sent, clickInProgress will return true, and clickCancel may be called to
     * cancel sending the click.
     *
     * @param button
     *     The button to click.
     */
    Touchview.prototype.click = function(button) {
        var self = this;
        var currentTouches = util.cloneTouches(this.currentTouches);

        // Make a short delay before sending the click event
        this._click = setTimeout(
            function() {
                var button = currentTouches.length == 2
                    ? 3
                    : 1;
                self.touchpad.buttonDown(button);
                self.touchpad.buttonUp(button);
                self._click = undefined;
            },
            300);
    };

    /**
     * Determines whether a click is queued to be sent.
     *
     * @return whether a click will be sent in the immediate future
     */
    Touchview.prototype.clickInProgress = function() {
        return !!this._click;
    }

    /**
     * Cancels the current click.
     *
     * @return whether the click was cancelled; this function will return false
     *     if no click is queued
     */
    Touchview.prototype.clickCancel = function() {
        if (this._click) {
            clearTimeout(this._click);
            this._click = undefined;
            return true;
        }
        else {
            return false;
        }
    }

    /**
     * Starts a DnD operation.
     *
     * This will send a button down event.
     */
    Touchview.prototype.dndStart = function() {
        this._dnd = true;
        this.touchpad.buttonDown(1);
    }

    /**
     * Determines whether a DnD operation is in progress.
     *
     * @return whether a DnD operation is in progress
     */
    Touchview.prototype.dndInProgress = function() {
        return !!this._dnd;
    }

    /**
     * Ends a DnD operation.
     *
     * This will send a button up event.
     */
    Touchview.prototype.dndEnd = function() {
        this._dnd = false;
        this.touchpad.buttonUp(1);
    }

    Touchview.prototype.onTouchStart = function(event) {
        this.currentTouches = util.cloneTouches(event.touches);

        this._hasMoved = false;

        event.preventDefault();
    };

    Touchview.prototype.onTouchEnd = function(event) {
        // Click if no move has been made
        if (!this._hasMoved) {
            if (this.dndInProgress()) {
                this.dndEnd();
            }
            else {
                this.click(this.currentTouches.length == 2
                    ? 3
                    : 1);
            }
        }

        delete this.currentTouches;
    };

    Touchview.prototype.onTouchCancel = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchLeave = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchMove = function(event) {
        this._hasMoved = true;

        // If this is the second click in a short period, treat this as DnD
        if (this.clickInProgress()) {
            this.clickCancel();
            this.dndStart();
        }

        if (!event.changedTouches) {
            return;
        }

        // Require all touches to be present
        if (event.changedTouches.length != this.currentTouches.length) {
            return;
        }

        // Locate touches that are interesting
        var oldTouch = this.currentTouches[0];
        var newTouch = event.changedTouches.identifiedTouch(
            oldTouch.identifier);

        // Replace the current touches
        this.currentTouches = util.cloneTouches(event.changedTouches);

        if (event.changedTouches.length == 1) {
            var movement = calculateMovement(oldTouch, newTouch);
            this.touchpad.move.apply(undefined, movement);
        }
        else if (event.changedTouches.length == 2) {
            var scroll = calculateScroll(oldTouch, newTouch);
            this.touchpad.scroll.apply(undefined, scroll);
        }

        event.preventDefault();
    };

    return module;
})();
