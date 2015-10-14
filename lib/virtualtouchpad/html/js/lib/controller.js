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
exports.controller = (function() {
    var module = {};

    /**
     * The touchpad controller.
     */
    function Touchpad(ws) {
        this.ws = ws;
    };
    module.Touchpad = Touchpad;

    /**
     * Simulates pressing a button.
     *
     * @param button
     *     The button name.
     */
    Touchpad.prototype.buttonDown = function(button) {
        this.ws.send(JSON.stringify({
            command: "mouse.down",
            data: {
                button: button}}));
    };

    /**
     * Simulates releasing a button.
     *
     * @param button
     *     The button name.
     */
    Touchpad.prototype.buttonUp = function(button) {
        this.ws.send(JSON.stringify({
            command: "mouse.up",
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
        this.ws.send(JSON.stringify({
            command: "mouse.scroll",
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
        this.ws.send(JSON.stringify({
            command: "mouse.move",
            data: {
                dx: dx,
                dy: dy}}));
    };

    /**
     * The keyboard controller.
     */
    function Keyboard(ws) {
        this.ws = ws;
    };
    module.Keyboard = Keyboard;

    /**
     * Simulates pressing a key.
     *
     * @param name
     *     The name of the key. This should typically be the actual character
     *     requested, or a key name enclosed in brackets ("<shift>").
     * @param isDead
     *     Whether this is a dead key press.
     */
    Keyboard.prototype.press = function(name, isDead) {
        this.ws.send(JSON.stringify({
            command: "key.down",
            data: {
                name: name,
                is_dead: isDead}}));
    };

    /**
     * Simulates releasing a key.
     *
     * @param name
     *     The name of the key. This should typically be the actual character
     *     requested, or a key name enclosed in brackets ("<shift>").
     * @param isDead
     *     Whether this is a dead key press.
     */
    Keyboard.prototype.release = function(name, isDead) {
        this.ws.send(JSON.stringify({
            command: "key.up",
            data: {
                name: name,
                is_dead: isDead}}));
    };

    return module;
})();
