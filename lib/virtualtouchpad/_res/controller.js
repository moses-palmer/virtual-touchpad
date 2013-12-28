exports.controller = (function() {
    var module = {};

    /**
     * The touchpad controller.
     */
    var Touchpad = function(ws) {
        this.ws = ws;
    };
    module.Touchpad = Touchpad;

    /**
     * Simulates pressing a button.
     *
     * @param button
     *     The button index.
     */
    Touchpad.prototype.buttonDown = function(button) {
        ws.send(JSON.stringify({
            command: "mouse_down",
            data: {
                button: button}}));
    };

    /**
     * Simulates releasing a button.
     *
     * @param button
     *     The button index.
     */
    Touchpad.prototype.buttonUp = function(button) {
        ws.send(JSON.stringify({
            command: "mouse_up",
            data: {
                button: button}}));
    };

    /**
     * Simulates scrolling.
     *
     * @param dx, dy
     *     The horizontal and vertical scroll.
     */
    Touchpad.prototype.scroll = function(dx, dy) {
        ws.send(JSON.stringify({
            command: "mouse_scroll",
            data: {
                dx: dx,
                dy: dy}}));
    };

    /**
     * Simulates moving the mouse.
     *
     * @param dx, dy
     *     The horizontal and vertical movement.
     */
    Touchpad.prototype.move = function(dx, dy) {
        ws.send(JSON.stringify({
            command: "mouse_move",
            data: {
                dx: dx,
                dy: dy}}));
    };

    return module;
})();

