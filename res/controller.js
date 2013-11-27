exports.controller = (function() {
    var module = {};

    /**
     * The touchpad controller.
     */
    var Touchpad = function(ws) {
        this.ws = ws;
    };
    module.Touchpad = Touchpad;

    return module;
})();
