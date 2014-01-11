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

    // Check for inline SVG support
    if (!document.implementation.hasFeature(
            "http://www.w3.org/TR/SVG11/feature#SVG", "1.1")
        && !document.implementation.hasFeature(
            "http://www.w3.org/TR/SVG11/feature#Image", "1.1")) {
        module.failures.push("SVG");
    }

    // Check for fullscreen support for the document element
    if (typeof(document.documentElement.requestFullscreen) === "undefined") {
        if (document.documentElement.mozRequestFullScreen) {
            document.documentElement.requestFullscreen =
                document.documentElement.mozRequestFullScreen;
            document.exitFullscreen = document.mozCancelFullScreen;
            document.FULLSCREENCHANGE_EVENT_NAME = "mozfullscreenchange";
            document.FULLSCREEN_ELEMENT_NAME = "mozFullScreenElement";
        }
        else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.requestFullscreen = function() {
                return document.documentElement.webkitRequestFullscreen(
                    Element.ALLOW_KEYBOARD_INPUT);
            };
            document.exitFullscreen = document.webkitExitFullscreen;
            document.FULLSCREENCHANGE_EVENT_NAME = "webkitfullscreenchange";
            document.FULLSCREEN_ELEMENT_NAME = "webkitFullscreenElement";
        }
        else {
            module.failures.push("Fullscreen");
        }
    }

    return module;
})();

