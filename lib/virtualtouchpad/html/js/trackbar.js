/******************************************************************************/
/* virtual-touchpad                                                           */
/* Copyright (C) 2013-2014 Moses Palmér                                       */
/*                                                                            */
/* This program is free software: you can redistribute it and/or modify it    */
/* under the terms of the GNU General Public License as published by the Free */
/* Software Foundation, either version 3 of the License, or (at your option)  */
/* any later version.                                                         */
/*                                                                            */
/* This program is distributed in the hope that it will be useful, but        */
/* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY */
/* or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License    */
/* for more details.                                                          */
/*                                                                            */
/* You should have received a copy of the GNU General Public License along    */
/* with this program. If not, see <http://www.gnu.org/licenses/>.             */
/******************************************************************************/
exports.trackbar = (function() {
    var module = {
        /**
         * The element type that is autmatically instantiated as a trackbar.
         */
        EL: "trackbar",

        /**
         * The class of the mark element of a trackbar.
         */
        MARK_CLASS: "trackbar-mark"};

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

        // Find or create the track element
        for (var i = 0; i < parentEl.childElementCount; i++) {
            var markEl = parentEl.children[i];
            if (markEl.classList.contains(module.MARK_CLASS)) {
                this.markEl = markEl;
                break;
            }
        }
        if (!this.markEl) {
            this.markEl = document.createElement("div");
            this.markEl.className = module.MARK_CLASS;
            this.parentEl.appendChild(this.markEl);
        }

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

        // Unfortunately we need to continuously update the view
        setInterval(this._refresh.bind(this), 100);
    };
    module.Trackbar = Trackbar;

    /**
     * Repositions the mark element to reflect the current value.
     */
    Trackbar.prototype._refresh = function() {
        var maxLeft = this.parentEl.clientWidth - this.markEl.clientWidth;
        this.markEl.style.left = (maxLeft
            * (this._value - this.minValue) / (this.maxValue - this.minValue))
                .toFixed(0) + "px";
    };

    /**
     * Returns the trackbar value for a given x coordinate of the track element.
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

        this._currentTouch = util.cloneTouches(event.touches)[0];

        // Set value
        this.setValue(this._xToValue(this._currentTouch.pageX));

        event.preventDefault();
    };

    Trackbar.prototype.onTouchEnd = function(event) {
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
    exports.onloadCallbacks.push(function() {
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

            // Register valuechanged event handlers
            var valuechanged = el.getAttribute("onvaluechanged");
            if (valuechanged) {
                el.addEventListener("valuechanged", (function(command) {
                    eval(command);
                }).bind(el.trackbar, valueChanged));
            }

            // If property is passed, bind this control to a configuration value
            var property = el.getAttribute("property");
            if (property) {
                el.addEventListener("valuechanged", (function(name) {
                    configuration.set(name, this.value())
                }).bind(el.trackbar, property));

                var defaultValue = eval(el.getAttribute("default-value"));
                if (isNaN(defaultValue)) {
                    defaultValue = value;
                }
                el.trackbar.setValue(configuration.get(property, defaultValue));
            }
        }
    });

    return module;
})();
