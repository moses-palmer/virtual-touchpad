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
         *     If the configuration value cannot be interpreted as this type, or
         *     does not exist, or its type is unsupported, this value is
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
                else {
                    return defaultValue;
                }

            case "number":
                if (!isNaN(parseFloat(value))) {
                    return parseFloat(value);
                }
                else {
                    return defaultValue;
                }

            case "string":
                if (value) {
                    return value.toString();
                }
                else {
                    return defaultValue;
                }

            default:
                return defaultValue;
            }
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
