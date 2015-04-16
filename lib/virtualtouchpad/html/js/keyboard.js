/******************************************************************************/
/* virtual-touchpad                                                           */
/* Copyright (C) 2013-2015 Moses Palmér                                       */
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
exports.keyboard = (function() {
    var module = {
        EL: "keyboard",

        /**
         * The element that contains all keys.
         */
        KEYS_ROOT_ELEMENT: "keys"
    };

    /**
     * The keyboard.
     */
    function Keyboard(parentEl, src) {
        this.parentEl = parentEl;
        this.doc = null;

        // Get the keyboard SVG
        var ajax = new XMLHttpRequest();
        ajax.open("GET", src, true);
        ajax.send();
        ajax.onload = (function(e) {
            // First parse the data into an SVG document
            var parser = new DOMParser();
            var doc = parser.parseFromString(ajax.responseText, "text/xml");

            // Insert the document into the DOM and get a reference to it
            parentEl.appendChild(doc.documentElement);
            this.svg = parentEl.querySelector("svg");

            // Get the element that contains all keys
            this.keys = this.svg.getElementById(module.KEYS_ROOT_ELEMENT);
        }).bind(this);
    };
    module.Keyboard = Keyboard;

    /**
     * Determines whether a DOM element represents a key.
     *
     * An element is considered as a key if its immediate parent is the element
     * with the ID module.KEYS_ROOT_ELEMENT.
     *
     * @param el
     *     The DOM element to check.
     * @return whether the element is a key
     */
    Keyboard.prototype._isKey = function isKey(el) {
        // All keys are part of the "keys" group
        return el.parentNode === this.keys;
    };

    /**
     * Retrieves the key at the specified position.
     *
     * @param row
     *     The row of the key.
     * @param col
     *     The column of the key.
     * @return the key element if it exists
     */
    Keyboard.prototype._getKey = function getKey(row, col) {
        return this.svg.querySelector(
            ".key[x-row='" + row + "'][x-col='" + col + "']");
    };

    /**
     * Calls callback for every key that is touched by on of the touches in
     * touches.
     *
     * @param touches
     *     A list of Touch instances.
     * @param callback
     *     The callback to call for each touch that is located over a key. This
     *     callback will be passed the parameters key, which is the key element,
     *     and touchID, which is the identifier of the Touch instance. If the
     *     touch does not hover above a key, null will be passed as key.
     */
    Keyboard.prototype._eachKey = function eachKey(touches, callback) {
        for (var i = 0; i < touches.length; i++) {
            var touch = touches[i];
            var el = document.elementFromPoint(touch.pageX, touch.pageY);
            while (el) {
                if (this._isKey(el)) {
                    break;
                }
                el = el.parentNode;
            }

            callback(el, touch.identifier);
        }
    };

    /**
     * Automatically instantiate all keyboards when the document is loaded.
     */
    exports.onloadCallbacks.push(function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            var src = el.getAttribute("src");

            el.keyboard = new Keyboard(el, src);
        }
    });

    return module;
})();
