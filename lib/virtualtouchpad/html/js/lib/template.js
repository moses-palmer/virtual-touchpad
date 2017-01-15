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
 * Replaces tokens on the format `${template.name}` in elements with the
 * attribute `x-tpl`.
 */
exports.template = (function() {
    var module = {
        /**
         * The attribute to set on elements that should have templates applied.
         */
        TEMPLATE_ATTR: "x-tpl",

        /**
         * The attribute used to store the original text content.
         */
        ORIGINAL_ATTR: "x-tpl-original"
    };

    /**
     * Applies templates to all elements marked with the template attribute.
     */
    function apply() {
        var els = elements();

        // Apply templates to all elements
        for (i = 0; i < els.length; i++) {
            var el = els[i];
            el.setAttribute(module.ORIGINAL_ATTR, el.innerHTML);
            el.innerHTML = el.innerHTML.format(
                util.mapSupplier(server.status));
        }
    };

    /**
     * Applies templates to all elements marked with the template attribute.
     */
    function update() {
        var els = elements();

        // Apply templates to all elements
        for (i = 0; i < els.length; i++) {
            var el = els[i];
            var data = el.getAttribute(module.ORIGINAL_ATTR) || el.innerHTML;
            el.innerHTML = data.format(
                util.mapSupplier(server.status));
        }
    };

    /**
     * Returns a list of templated elements.
     *
     * @return an array of elements
     */
    function elements() {
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

        return els;
    }

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

    // We require the status library to be loaded
    document.addEventListener("statusload", callbacks);
    document.addEventListener("statusupdate", update);
    callbacks.remaining++;

    // Ensure translations are applied before we apply templates
    document.addEventListener("translated", callbacks);
    callbacks.remaining++;

    // The libraries may not have been loaded; if the translation library is not
    // loaded, we automatically decreases the number of remaining callbacks
    addEventListener("load", function() {
        if (!exports.translation) {
            callbacks();
        }
    });

    return module;
})();
