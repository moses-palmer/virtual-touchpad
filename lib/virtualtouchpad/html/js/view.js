exports.view = (function() {
    var module = {};

    /**
     * The touchpad view.
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
     * Clones an array of touches keeping only identifier, screenX and screenY.
     *
     * @param touches
     *     A TouchList to clone. If this is falsy, [] is returned.
     * @return an array of objects
     */
    function cloneTouches(touches) {
        if (!touches) return [];

        var result = [];

        for (var i = 0; i < touches.length; i++) {
            result.push({
                identifier: touches[i].identifier,
                screenX: touches[i].screenX,
                screenY: touches[i].screenY});
        }

        return result;
    }

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

        // TODO: Make configurable
        var acceleration = 0.3;
        var sensitivity = 1.5;

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

        // TODO: Make configurable
        var xdirection = -1;
        var ydirection = -1;

        return [
            dx > 0
                ? xdirection
                : dx < 0
                    ? -xdirection
                    : 0,
            dy > 0
                ? ydirection
                : dy < 0
                    ? -ydirection
                    : 0];
    }

    Touchview.prototype.onTouchStart = function(event) {
        this.currentTouches = cloneTouches(event.touches);

        this.hasMoved = false;

        event.preventDefault();
    };

    Touchview.prototype.onTouchEnd = function(event) {
        // Click if no move has been made
        if (!this.hasMoved) {
            var button = this.currentTouches.length == 2
                ? 3
                : 1;
            this.touchpad.buttonDown(button);
            this.touchpad.buttonUp(button);
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
        this.hasMoved = true;

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
        this.currentTouches = cloneTouches(event.changedTouches);

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

