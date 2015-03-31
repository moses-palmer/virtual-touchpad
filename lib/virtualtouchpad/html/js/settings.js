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

        show: function() {
            overlay.classList.add(module.TOGGLED_CLASS);
            view.classList.add(module.TOGGLED_CLASS);
        },

        hide: function() {
            overlay.classList.remove(module.TOGGLED_CLASS);
            view.classList.remove(module.TOGGLED_CLASS);
        }};

    /**
     * Locate the overlay element.
     */
    exports.onloadCallbacks.push(function() {
        overlay = document.getElementById("settings-overlay");
        overlay.onclick = module.hide;

        view = document.getElementById("settings-view");
        view.addEventListener("touchstart", function(e) {
            e.preventDefault();
        });
    });

    return module;
})();
