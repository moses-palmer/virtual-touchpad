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
exports.include = (function() {
    var module = {
        EL: "x-include"};

    /**
     * The include element.
     */
    function Include(parentEl, href) {
        // Get the external XML
        var ajax = new XMLHttpRequest();
        ajax.open("GET", src, true);
        ajax.send();
        ajax.onload = (function(e) {
            // First parse the data into a document
            var parser = new DOMParser();
            var doc = parser.parseFromString(ajax.responseText, "text/xml");

            // Insert the document into the DOM
            parentEl.parentNode.insertBefore(doc.documentElement, parentEl)
            parentEl.parentNode.removeChild(parentEl);
        }).bind(this);
    };
    module.Include = Include;

    /**
     * Automatically replace all x-include with the XML from their href
     * attribute.
     */
    addEventListener("load", function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) (function(el) {
            var href = el.getAttribute("href");
            var ajax = new XMLHttpRequest();
            ajax.open("GET", href, true);
            ajax.send();
            ajax.onload = function(e) {
                // First parse the data into a document
                var parser = new DOMParser();
                var doc = parser.parseFromString(
                    ajax.responseText,
                    "text/xml");

                // Insert the document into the DOM
                el.parentNode.insertBefore(doc.documentElement, el)
                el.parentNode.removeChild(el);
            };
        })(els[i]);
    });

    return module;
})();
