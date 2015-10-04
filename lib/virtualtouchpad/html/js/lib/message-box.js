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
exports.messagebox = (function() {
    var module = {
        /**
         * The class that must be set on a parent element for the message box to
         * be visible.
         */
        MESSAGE_BOX_CLASS: "message-box"
    };

    /**
     * Displays the message box.
     *
     * @param message
     *     The message to display. This may be either a string, which will be
     *     displayed verbatim, or an element, which will be set as the child of
     *     the message box.
     * @param classes
     *     A list of classes to use for the message box.
     */
    module.show = function(message, classes) {
        var mbox = document.getElementById("message-box");

        // Remove all previous content
        while (mbox.firstChild) {
            mbox.removeChild(mbox.firstChild);
        }

        // Add the message
        if (typeof(message) === "string") {
            mbox.innerHTML = message;
        }
        else {
            mbox.appendChild(message);
        }

        // Add the classes and show the element
        mbox.className = classes.join(", ");
        document.documentElement.classList.add(module.MESSAGE_BOX_CLASS);
    };

    return module;
})();
