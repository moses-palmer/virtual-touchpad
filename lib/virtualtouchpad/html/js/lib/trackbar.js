/*****************************************************************************/
/* virtual-touchpad                                                          */
/* Copyright (C) 2013-2015 Moses Palmér                                      */
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
exports.trackbar = (function() {
    var module = {
        /**
         * The element type that is autmatically instantiated as a trackbar.
         */
        EL: "trackbar",

        /**
         * The class that is added to the track element when the trackbar is
         * being modified by the user.
         */
        ACTIVE_CLASS: "active",

        /**
         * The class of the track element of a trackbar.
         */
        TRACK_CLASS: "track",

        /**
         * The class of the groove element of a trackbar.
         */
        GROOVE_CLASS: "groove",

        /**
         * The class of the mark element of a trackbar.
         */
        MARK_CLASS: "mark"};

    /**
     * The trackbar.
     *
     * @param parentEl
     *     The trackbar element.
     * @param value
     *     The current value of the Trackbar.
     * @param minValue, maxValue
     *     The minimum and maximum value of the Trackbar
     */
    function Trackbar(parentEl, value, minValue, maxValue) {
        this.parentEl = parentEl;
        this._value =
            value < minValue
                ? minValue
                : value > maxValue
                    ? maxValue
                    : value;
        this.minValue = minValue;
        this.maxValue = maxValue;

        // Create the track elements
        this.trackEl = document.createElement("div");
        this.trackEl.classList.add(module.TRACK_CLASS);
        this.parentEl.appendChild(this.trackEl);

        this.grooveEl = document.createElement("div");
        this.grooveEl.classList.add(module.GROOVE_CLASS);
        this.trackEl.appendChild(this.grooveEl);

        this.markEl = document.createElement("div");
        this.markEl.classList.add(module.MARK_CLASS);
        this.grooveEl.appendChild(this.markEl);

        // Add event listeners
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
    };
    module.Trackbar = Trackbar;

    /**
     * Repositions the mark element to reflect the current value.
     */
    Trackbar.prototype._refresh = function() {
        var v = (this._value - this.minValue) / (
            this.maxValue - this.minValue);
        this.grooveEl.style.width = (v * 100).toFixed(0) + "%";
    };

    /**
     * Returns the trackbar value for a given x coordinate of the track
     * element.
     *
     * @param x
     *     The x coordinate of the centre of the track element in viewport
     *     coordinates.
     * @return a value which may be outside the bounds
     *     [this.minValue..this.maxValue]
     */
    Trackbar.prototype._xToValue = function(x) {
        var d = this.maxValue - this.minValue;
        return this.minValue
            + (x - this.parentEl.position()[0] - this.markEl.clientWidth / 2)
                * d / (this.parentEl.clientWidth - this.markEl.clientWidth);
    };

    /**
     * Returns the current value of the trackbar.
     *
     * @return a value between minValue and maxValue
     */
    Trackbar.prototype.value = function() {
        return this._value;
    };

    /**
     * Sets the current value of the trackbar.
     *
     * @param value
     *     The value to set. This is clamped to be between minValue and
     *     maxValue.
     */
    Trackbar.prototype.setValue = function(value) {
        this._value = value < this.minValue
            ? this.minValue
            : value > this.maxValue
                ? this.maxValue
                : value;
        this._refresh();
        this.parentEl.dispatchEvent(new CustomEvent(
            "valuechanged",
            {
                value: this._value}));
    };

    Trackbar.prototype.onTouchStart = function(event) {
        // Ignore multi-finger touches
        if (event.touches.length > 1) {
            return;
        }

        this.parentEl.classList.add(module.ACTIVE_CLASS);
        this._currentTouch = util.cloneTouches(event.touches)[0];

        // Set value
        this.setValue(this._xToValue(this._currentTouch.pageX));

        event.preventDefault();
    };

    Trackbar.prototype.onTouchEnd = function(event) {
        this.parentEl.classList.remove(module.ACTIVE_CLASS);
        this._currentTouch = undefined;

        event.preventDefault();
    };

    Trackbar.prototype.onTouchCancel = function(event) {
        // TODO: Implement
    };

    Trackbar.prototype.onTouchLeave = function(event) {
        // TODO: Implement
    };

    Trackbar.prototype.onTouchMove = function(event) {
        if (!this._currentTouch || !event.changedTouches) {
            return;
        }

        // Get the x position
        var touch = event.changedTouches.identifiedTouch(
            this._currentTouch.identifier);
        if (!touch) {
            return;
        }
        var x = touch.pageX;

        // Update the trackbar
        this.setValue(this._xToValue(x));

        event.preventDefault();
    };

    /**
     * Finds all Trackbar instances by CSS selector.
     *
     * @param selector
     *     The CSS selector to use.
     * @return a list of Trackbar instances
     */
    module.find = function(selector) {
        var els = document.querySelectorAll(selector);
        var result = [];

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            if (el.trackbar) {
                result.push(el.trackbar);
            }
        }

        return result;
    };

    /**
     * Automatically instantiate all trackbars when the document is loaded.
     */
    addEventListener("load", function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            // Read the current value from the element
            var value = eval(el.getAttribute("value"));
            if (isNaN(value)) {
                value = 0.0;
            }

            // Read the min and max values from the element
            var minValue = eval(el.getAttribute("min-value"));
            if (isNaN(minValue)) {
                minValue = 0.0;
            }
            var maxValue = eval(el.getAttribute("max-value"));
            if (isNaN(maxValue)) {
                maxValue = minValue + 1.0;
            }

            el.trackbar = new Trackbar(el, value, minValue, maxValue);

            // Register event handlers
            el.handleEvent("valuechanged");

            // If property is passed, bind this control to a configuration
            // value
            var property = el.getAttribute("property");
            if (property) {
                el.addEventListener("valuechanged", (function(property) {
                    configuration.set(property, this.value())
                }).bind(el.trackbar, property));

                var defaultValue = eval(el.getAttribute("default-value"));
                if (isNaN(defaultValue)) {
                    defaultValue = value;
                }
                el.trackbar.setValue(
                    configuration.get(property, defaultValue));
            }
        }
    });

    return module;
})();
