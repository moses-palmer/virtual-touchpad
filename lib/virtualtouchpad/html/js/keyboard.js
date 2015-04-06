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
        EL: "keyboard"};

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
        }).bind(this);
    };
    module.Keyboard = Keyboard;

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
