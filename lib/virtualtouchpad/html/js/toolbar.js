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
exports.toolbar = (function() {
    var module = {
        /**
         * The element type that is automatically instantiated as a toolbar.
         */
        EL: "toolbar"};

    /**
     * The toolbar.
     */
    function Toolbar(parentEl) {
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
     * Applies styles necessary for this type of toolbar class.
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
                hiddenBottom = -(4 * this.parentEl.clientHeight / 6);

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
                    : bottom > hiddenBottom
                        ? bottom
                        : hiddenBottom) + "px";

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
                if (t > 0.95) {
                    t = 1.0;
                }
                else if (t < 0.05) {
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
            throw "Unknown toolbar type";
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

    /**
     * Finds all Toolbar instances by CSS selector.
     *
     * @param selector
     *     The CSS selector to use.
     * @return a list of Toolbar instances
     */
    module.find = function(selector) {
        var els = document.querySelectorAll(selector);
        var result = [];

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            if (el.toolbar) {
                result.push(el.toolbar);
            }
        }

        return result;
    };

    /**
     * Automatically instantiate all toolbars when the document is loaded.
     */
    exports.onloadCallbacks.push(function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];
            el.toolbar = new Toolbar(el);

            // Hide the toolbar after a while
            setTimeout(el.toolbar.hide.bind(el.toolbar), 2000);
        }
    });

    return module;
})();
