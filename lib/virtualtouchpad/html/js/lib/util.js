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
exports.util = (function() {
    var module = {};

    /**
     * Clones an array of touches keeping only identifier, screenX, screenY,
     * clientX and clientY.
     *
     * @param touches
     *     A TouchList to clone. If this is falsy, [] is returned.
     * @return an array of objects
     */
    module.cloneTouches = function(touches) {
        if (!touches) return [];

        var result = [];

        for (var i = 0; i < touches.length; i++) {
            result.push({
                identifier: touches[i].identifier,
                screenX: touches[i].screenX,
                screenY: touches[i].screenY,
                clientX: touches[i].clientX,
                clientY: touches[i].clientY});
        }

        return result;
    };

    /**
     * XML escapes a string.
     */
    String.prototype.xmlEscape = function() {
        return this.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&apos;');
    };

    /**
     * Returns the position of an element, relative to the viewport.
     *
     * @return the array [x, y]
     */
    Element.prototype.position = function() {
        var x = 0;
        var y = 0;

        var o = this;
        while (true) {
            x += o.offsetLeft;
            y += o.offsetTop;
            if (o.offsetParent === null){
                break;
            }
            o = o.offsetParent;
        }

        return [x, y];
    };

    /**
     * Automatically attaches an event handler for a named event from an
     * attribute value.
     *
     * @param event
     *     The name of the event. The attribute must be "on" + event.
     */
    Element.prototype.handleEvent = function(event) {
        var value = this.getAttribute("on" + event);
        if (value) {
            this.addEventListener(
                event,
                function(event) {
                    eval(value);
                });
        }
    };

    return module;
})();
