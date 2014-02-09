exports.configuration = (function() {
    var module = {
        _storage: {}};

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

