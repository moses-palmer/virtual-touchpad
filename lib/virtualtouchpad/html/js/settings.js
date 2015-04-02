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
exports.settings = (function() {
    var overlay, view;
    var module = {
        /**
         * The name of the class added to the settings view and overlay when it
         * should be shown.
         */
        TOGGLED_CLASS: "toggled",

        /**
         * The name of the class added to the settings view and overlay when it
         * is sliding.
         */
        SLIDING_CLASS: "sliding",

        show: function() {
            overlay.classList.add(module.TOGGLED_CLASS);
            view.classList.add(module.TOGGLED_CLASS);
        },

        visible: function() {
            return view.classList.contains(module.TOGGLED_CLASS);
        },

        slideBegin: function() {
            view.classList.add(module.SLIDING_CLASS);
        },

        slideEnd: function() {
            view.classList.remove(module.SLIDING_CLASS);
        },

        hide: function() {
            overlay.classList.remove(module.TOGGLED_CLASS);
            view.classList.remove(module.TOGGLED_CLASS);
        }};

    /**
     * Locate the overlay element.
     */
    exports.onloadCallbacks.push(function() {
        var firstTouch, currentTouch;
        var i = 0;

        function dx(touch) {
            return touch.screenX - firstTouch.screenX;
        }

        overlay = document.getElementById("settings-overlay");
        overlay.addEventListener("touchstart", function(event) {
            module.slideBegin();

            // Make sure we have a description of the first touch
            firstTouch = util.cloneTouches(event.touches)[0];
        });
        overlay.addEventListener("touchmove", function(event) {
            // Find the new incarnation of the original touch
            var c = currentTouch = event.changedTouches.identifiedTouch(
                firstTouch.identifier);
            if (!c) {
                return;
            }
            currentTouch = c;

            // Slide the view, and make sure to snap it to the edge
            var d = dx(currentTouch).toFixed(0);
            if (d > 0) d = 0;
            view.style.marginLeft = d + "px";
        });
        overlay.addEventListener("touchend", function(e) {
            var d = dx(currentTouch) / view.clientWidth;
            if (d < -0.15) {
                module.hide();
            }
            else if (d > 0.5) {
                module.show();
            }
            else {
                if (module.visible()) {
                    module.show();
                }
                else {
                    module.hide();
                }
            }

            // Make sure to remove the explicitly set style to allow the CSS to
            // decide
            view.removeAttribute("style");

            module.slideEnd();
        });

        view = document.getElementById("settings-view");
        view.addEventListener("touchstart", function(e) {
            e.preventDefault();
        });
    });

    return module;
})();
