/*****************************************************************************/
/* virtual-touchpad                                                          */
/* Copyright (C) 2013-2017 Moses Palmér                                      */
/*                                                                           */
/* This program is free software: you can redistribute it and/or modify it   */
/* under the terms of the GNU General Public License as published by the     */
/* Free Software Foundation, either version 3 of the License, or (at your    */
/* option) any later version.                                                */
/*                                                                           */
/* This program is distributed in the hope that it will be useful, but       */
/* WITHOUT ANY WARRANTY; without even the implied warranty of                */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General  */
/* Public License for more details.                                          */
/*                                                                           */
/* You should have received a copy of the GNU General Public License along   */
/* with this program. If not, see <http://www.gnu.org/licenses/>.            */
/*****************************************************************************/
/**
 * The touch view component.
 *
 * All elements of the type `view.EL` will be replaced with actual touch views.
 *
 * A touch view provides events compatible with what a mouse controller expects.
 * The events are propagated as DOM events. The following events are supported:
 *
 * `buttondown`, `buttonup`
 *     A button has been pressed or released. The detail contains the name of
 *     the button.
 * `move`
 *     The mouse pointer has been moved. The detail contains the value
 *     `[dx, dy]`, which is the horisontal and vertical movements.
 * `scroll`
 *     Scrolling or panning is being performed. The detail contains the value
 *     `[dx, dy]`, which is the horisontal and vertical movements.
 *
 * A touch view uses the following configuration properties:
 *
 * `view.acceleration`
 *     The acceleration to apply to movements. Increasing this value will make
 *     greater movements have greater impact.
 * `view.naturalScroll`
 *     Whether to use natural scroll. When this is active, panning on the touch
 *     view gives the impression of dragging the view on screen.
 * `view.sensitivity`
 *     The basic sensitivity. This is a value applied to all movements.
 */
exports.view = (function() {
    var module = {
        EL: "x-touchpad",

        /**
         * The maximum accumulated movement where touch-and-release is
         * considered as a click.
         */
        CLICK_THRESHOLD: 10};

    /**
     * The touchpad view.
     *
     * @param touchpad
     *     The controller to use.
     */
    function Touchview(parentEl) {
        this.parentEl = parentEl;

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
     * Calculates the movement vector given the old and new touch events.
     *
     * @param oldTouch, newTouch
     *     The previous and current touch events.
     * @return the movement vector [dx, dy]
     */
    Touchview.prototype._calculateMovement = function(oldTouch, newTouch) {
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
    Touchview.prototype._calculateScroll = function(oldTouch, newTouch) {
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
     * If a click is in progress, no action is performed.
     *
     * @param button
     *     The button to click.
     */
    Touchview.prototype.click = function(button) {
        // Do nothing if a click is in progress
        if (this.clickInProgress()) {
            return;
        }

        var currentTouches = util.cloneTouches(this.currentTouches);

        // Make a short delay before sending the click event
        this._click = setTimeout(
            (function() {
                var button = currentTouches.length == 2
                    ? "right"
                    : "left";
                this.parentEl.dispatchEvent(new CustomEvent(
                    "buttondown",
                    {"detail": [button]}));
                this.parentEl.dispatchEvent(new CustomEvent(
                    "buttonup",
                    {"detail": [button]}));
                delete this._click;
            }).bind(this),
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
        this.parentEl.dispatchEvent(new CustomEvent(
            "buttondown",
            {"detail": ["left"]}));
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
        this.parentEl.dispatchEvent(new CustomEvent(
            "buttonup",
            {"detail": ["left"]}));
    }

    Touchview.prototype.onTouchStart = function(event) {
        this.currentTouches = util.cloneTouches(event.touches);

        this._accumulatedMovement = 0;

        event.preventDefault();
    };

    Touchview.prototype.onTouchEnd = function(event) {
        // Click if not enough movement has been made
        if (this._accumulatedMovement < module.CLICK_THRESHOLD) {
            if (this.dndInProgress()) {
                this.dndEnd();
            }
            else {
                this.click(this.currentTouches.length == 2
                    ? "right"
                    : "left");
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
        this._accumulatedMovement += Math.sqrt(0
            + Math.pow(newTouch.screenX - oldTouch.screenX, 2)
            + Math.pow(newTouch.screenY - oldTouch.screenY, 2))

        // Replace the current touches
        this.currentTouches = util.cloneTouches(event.changedTouches);

        if (event.changedTouches.length == 1) {
            var movement = this._calculateMovement(oldTouch, newTouch);
            this.parentEl.dispatchEvent(new CustomEvent(
                "move",
                {"detail": movement}));
        }
        else if (event.changedTouches.length == 2) {
            var scroll = this._calculateScroll(oldTouch, newTouch);
            this.parentEl.dispatchEvent(new CustomEvent(
                "scroll",
                {"detail": scroll}));
        }

        event.preventDefault();
    };

    /**
     * Automatically instantiate all touch views when the document is loaded.
     */
    addEventListener("load", function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            el.touchview = new Touchview(el);

            // Automatically attach the event handlers
            el.handleEvent("buttondown");
            el.handleEvent("buttonup");
            el.handleEvent("move");
            el.handleEvent("scroll");
        }
    });

    return module;
})();
