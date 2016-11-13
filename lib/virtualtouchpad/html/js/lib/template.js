/*****************************************************************************/
/* virtual-touchpad                                                          */
/* Copyright (C) 2013-2016 Moses Palmér                                      */
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
 * Replaces tokens on the format `${template.name}` in elements with the
 * attribute `x-tpl`.
 */
exports.template = (function() {
    var module = {
        /**
         * The attribute to set on elements that should have templates applied.
         */
        TEMPLATE_ATTR: "x-tpl"
    };

    /**
     * Applies templates to all elements marked with the template attribute.
     */
    function apply() {
        // Find all elements with the x-tpl attribute
        var xpathResult = document.evaluate(
            "//*[@" + module.TEMPLATE_ATTR + "]",
            document,
            null,
            XPathResult.ANY_TYPE,
            null);

        // Store the elements in a list
        var i;
        var els = [];
        while (i = xpathResult.iterateNext()) {
            i.normalize();
            els.push(i);
        }

        // Apply templates to all elements
        for (i = 0; i < els.length; i++) {
            var el = els[i];
            el.textContent = el.textContent.format(module.supplier);
        }
    };

    /**
     * Decreases the  number of remaining callbacks and, if it reaches 0, calls
     * `apply`.
     */
    function callbacks() {
        callbacks.remaining--;
        if (callbacks.remaining == 0) {
            apply();
        }
    }
    callbacks.remaining = 0;

    // Always wait for the document to load
    addEventListener("load", function() {
        callbacks();
    });
    callbacks.remaining++;

    // Get the server status
    var ajax = new XMLHttpRequest();
    ajax.open("GET", "/status", true);
    ajax.send();
    ajax.onload = function(e) {
        module.supplier = util.mapSupplier(JSON.parse(ajax.responseText));
        callbacks();
    };
    callbacks.remaining++;

    // If the translation library has been loaded, ensure translations are
    // applied before we apply templates
    if (exports.translation) {
        document.addEventListener("translated", callbacks);
        callbacks.remaining++;
    }

    return module;
})();
