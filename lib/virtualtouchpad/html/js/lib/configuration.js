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
exports.configuration = (function() {
    var module = {
        _storage: {},

        /**
         * Reads a configuration value.
         *
         * This function supports booleans, numbers and strings.
         *
         * @param name
         *     The name of the configuration value.
         * @param defaultValue
         *     The value to use if the value is not stored.
         *
         *     This value determines the return type of this function. If this
         *     is not passed, a string is returned, otherwise a value with the
         *     same type is returned.
         *
         *     If the configuration value cannot be interpreted as this type,
         *     or does not exist, or its type is unsupported, this value is
         *     returned.
         * @return the parsed configuration value
         */
        get: function(name, defaultValue) {
            var value = read(name);

            switch (typeof(defaultValue)) {
            case "boolean":
                if (value === "true") {
                    return true;
                }
                else if (value === "false") {
                    return false;
                }
                break;

            case "number":
                if (!isNaN(parseFloat(value))) {
                    return parseFloat(value);
                }
                break;

            case "string":
                if (value) {
                    return value.toString();
                }
                break;
            }
            return defaultValue;
        },

        /**
         * Sets a configuration value.
         *
         * @param name
         *     The name of the configuration value.
         * @param value
         *     The value to set.
         */
        set: function(name, value) {
            write(name, value);
        }};

    var read = checks.failed("WebStorage")
        ? function(name) {
            return module._storage[name];
        }
        : function(name) {
            return localStorage[name];
        };

    var write = checks.failed("WebStorage")
        ? function(name, value, transient) {
            module._storage[name] = value.toString();
        }
        : function(name, value) {
            localStorage[name] = value;
        };

    return module;
})();
