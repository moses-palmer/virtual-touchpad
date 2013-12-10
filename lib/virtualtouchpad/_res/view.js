exports.view = (function() {
    var module = {};

    /**
     * The touchpad view.
     */
    var Touchview = function(parentEl, touchpad) {
        this.parentEl = parentEl;
        this.touchpad = touchpad;

        var self = this;
        this.parentEl.addEventListener("touchstart", function() {
            return self.onTouchStart.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchend", function() {
            return self.onTouchEnd.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchcancel", function() {
            return self.onTouchCancel.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchleave", function() {
            return self.onTouchEnd.apply(self, arguments);
        });
        this.parentEl.addEventListener("touchmove", function() {
            return self.onTouchMove.apply(self, arguments);
        });
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
     * Locates the touch with the specified identifier in a touch list.
     *
     * @param touches
     *     A TouchList in which to find the touch. If this is falsy, undefined
     *     is returned.
     * @param identifier
     *     The identifier of the touch to find.
     * @return a touch, or undefined if it was not found
     */
    function findTouch(touches, identifier) {
        if (!touches) return undefined;

        for (var i = 0; i < touches.length; i++) {
            if (touches[i].identifier === identifier) {
                return touches[i];
            }
        }
    }

    /**
     * Calculates the movement vector given the old and new touch events.
     *
     * @param oldTouch, newTouch
     *     The previous and current touch events.
     * @return the movement vector [dx, dy]
     */
    function calculateMovement(oldTouch, newTouch) {
        // TODO: Apply acceleration
        var dx = newTouch.screenX - oldTouch.screenX;
        var dy = newTouch.screenY - oldTouch.screenY;

        return [dx, dy];
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

        return [
            dx > 0
                ? 1
                : dx < 0
                    ? -1
                    : 0,
            dy > 0
                ? -1
                : dy < 0
                    ? 1
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
        var newTouch = findTouch(event.changedTouches, oldTouch.identifier);

        // Replace the current touches
        this.currentTouches = event.changedTouches;

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
