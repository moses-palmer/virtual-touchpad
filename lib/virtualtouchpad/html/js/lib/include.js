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
 * Dynamically loaded resources.
 *
 * All elements of the type `include.EL` will be loaded after the main document
 * has been loaded, parsed as XML and the inserted at the location of the
 * `x-include` element. The arrtribute `href` is used to specify the location.
 */
exports.include = (function() {
    var module = {
        EL: "x-include"};

    /**
     * The include element.
     */
    function Include(parentEl, href) {
        this.parentEl = parentEl;
        this.href = href;
        this.reload();
    };
    module.Include = Include;

    /**
     * Loads the resource and replaces the `x-include` element.
     */
    Include.prototype.reload = function() {
        // Get the external XML
        var ajax = new XMLHttpRequest();
        ajax.open("GET", this.href, true);
        ajax.send();
        ajax.onload = (function(e) {
            // Verify that we got a valid response
            if (ajax.responseCode < 200 || ajax.responseCode >= 300) {
                return;
            }

            // First parse the data into a document
            var parser = new DOMParser();
            var doc = parser.parseFromString(ajax.responseText, "text/xml");

            var previousEl = this.parentEl;
            var nextEl = doc.documentElement;

            this.parentEl = nextEl;
            nextEl.include = this;
            nextEl.setAttribute(
                "id",
                previousEl.getAttribute("id"));

            // Insert the document into the DOM
            previousEl.parentNode.insertBefore(nextEl, previousEl)
            previousEl.parentNode.removeChild(previousEl);
        }).bind(this);
    };

    /**
     * Automatically replace all x-include with the XML from their href
     * attribute.
     */
    addEventListener("load", function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];
            var href = el.getAttribute("href");
            var include = new Include(el, href);
            el.include = include;
        }
    });

    return module;
})();
