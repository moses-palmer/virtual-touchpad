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
    if (typeof(WebSocket) == "undefined") {
        module.failures.push("WebSocket");
    }

    // Check for touch events and make sure TouchList has the "identifiedTouch"
    // method
    if (!("ontouchstart" in window)) {
        module.failures.push("TouchEvents");
    }
    else {
        if (typeof(TouchList.prototype.identifiedTouch) == "undefined") {
            TouchList.prototype.identifiedTouch = function(identifier) {
                for (var i = 0; i < this.length; i++) {
                    if (this[i].identifier === identifier) {
                        return this[i];
                    }
                }
            };
        }
    }

    return module;
})();

