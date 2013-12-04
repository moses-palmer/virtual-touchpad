exports.checks = (function() {
    var module = {
        failures: []};

    /**
     * Determines whether a check has failed.
     *
     * A check that has not been performed has not failed.
     *
     * @param check
     *     The name of the check.
     * @return whether the check failed
     */
    module.failed = function(check) {
        return module.failures.indexOf(check) != -1;
    }

    // Check for WebSocket
    if (typeof(WebSocket) !== "function") {
        module.failures.push("WebSocket");
    }

    // Check for touch events
    if (!("ontouchstart" in window)) {
        module.failures.push("TouchEvents");
    }

    return module;
})();
