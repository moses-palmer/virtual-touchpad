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
 * Provides runtime translation services.
 *
 * This module expects the translations to be loaded during page load, but after
 * this module, and added to `translation.catalog`. Please see
 * `translation.translate` and `translation.translateN` for the expected format.
 *
 * All elements with the attribute `translation.TRANSLATION_ATTRIBUTE` will be
 * translated after the main document has been loaded.
 */
exports.translation = (function() {
    var module = {
        /**
         * The attribute that signifies that an element should be translated.
         */
        TRANSLATION_ATTRIBUTE: "x-tr"};

    /**
     * Ensures that a string can be compared with the `innerHTML` of an element.
     *
     * This function creates an empty tag, sets its `innerHTML` to `s` and then
     * returns the generated `innerHTML`.
     *
     * @param s
     *     The string to wrap.
     */
    function wrap(s) {
        var el = document.createElement("t");
        el.innerHTML = s.trim().replace(/\s+/g, " ");
        return el.innerHTML;
    }

    /**
     * Gets the catalogue entry for a string.
     *
     * @param k
     *     The catalogue entry key.
     * @return the catalogue entry, or nothing if no catalogue is loaded
     */
    module.get = function(k) {
        if (module.catalog && module.catalog.texts) {
            return module.catalog.texts[wrap(k)];
        }
    };

    /**
     * Translates a string into the current language.
     *
     * @param s
     *     The string to translate.
     * @return a translated string, or s if no translation exists
     */
    module.translate = function(s) {
        return module.get(s) || s;
    };

    /**
     * Translates a plural string into the current language.
     *
     * @param s
     *     The string to translate for plural index 0.
     * @param ...
     *     The other plural strings of the original language followed by the
     *     numeral.
     * @return a translated string, or the original if no translation exists
     */
    module.translateN = function(s) {
        var n = arguments[arguments.length - 1];
        var i = module.pluralizer(n);
        var c = module.get(s);
        if (c instanceof Array) {
            return c[i];
        }
        else {
            return arguments[i];
        }
    };

    /**
     * Initialise the pluraliser from the string in the catalogue.
     */
    addEventListener("load", function() {
        /**
         * The function used to turn numerals into text indice.
         *
         * @param n
         *     The numeral.
         * @return an index into a plural translation, or nothing if no
         *     catalogue is loaded
         */
        module.pluralizer = function(n) {
            if (!module.catalog) {
                return;
            }
            var result = eval(module.catalog.plural);
            if (result === true) {
                return 1;
            }
            else if (result === false) {
                return 0;
            }
            else if (typeof(result) == "number") {
                return result;
            }
            else {
                throw "Invalid plural value: " + result;
            }
        };

        // Wrap all texts to sanitise lookups
        if (module.catalog && module.catalog.texts) {
            var texts = {}
            for (var k in module.catalog.texts) {
                if (module.catalog.texts.hasOwnProperty(k)) {
                    texts[wrap(k)] = module.catalog.texts[k];
                }
            }

            module.catalog.texts = texts;
        }

        // Find all elements with the x-tr attribute
        var xpathResult = document.evaluate(
            "//*[@" + module.TRANSLATION_ATTRIBUTE + "]",
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

        // Translate the text of all elements
        for (i = 0; i < els.length; i++) {
            els[i].innerHTML = module.translate(
                els[i].innerHTML.trim().split(/\s+/).join(" "));
        }

        // Dispacth the 'translated' event
        document.dispatchEvent(new CustomEvent("translated", {}))
    });

    return module;
})();

_ = exports.translation.translate;
_N = exports.translation.translateN;
