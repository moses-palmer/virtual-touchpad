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

    Touchview.prototype.onTouchStart = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchEnd = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchCancel = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchLeave = function(event) {
        // TODO: Implement
    };

    Touchview.prototype.onTouchMove = function(event) {
        // TODO: Implement
    };

    return module;
})();
