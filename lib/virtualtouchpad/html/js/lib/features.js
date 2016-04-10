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
exports.features = (function() {
    var module = {};

    /**
     * Shows a modal message box with missing features if any required features
     * are mising, otherwise does nothing.
     *
     * @return whether any required features were missing
     */
    module.listMissing = function() {
        var list = document.createDocumentFragment();

        /**
         * Inserts an error message.
         *
         * @param message
         *     The error message.
         */
        function insertError(message) {
            var li = document.createElement("li");
            li.innerHTML = message;
            list.appendChild(li);
        }

        // We need WebSocket support to even send messages to the server
        if (checks.failed("WebSocket")) {
            insertError(_(
                "WebSockets are not supported"));
        }

        // We need touch events to simulate touchpad
        if (checks.failed("TouchEvents")) {
            insertError(_(
                "Touch events are not supported"));
        }

        // We need SVG for the user interface
        if (checks.failed("SVG")) {
            insertError(_(
                "SVG images are not supported"));
        }

        // If any checks failed, add them to the displayed list
        if (list.childNodes.length > 0) {
            var message = document.createDocumentFragment();
            message.appendChild(document.createTextNode(_(
                "Your browser does not support Virtual Touchpad. These "
                + "features are missing:")));
            var ul = document.createElement("ul");
            ul.appendChild(list);
            message.appendChild(ul);
            message.appendChild(document.createTextNode(_(
                "Please upgrade your browser to a newer version.")));

            messagebox.show(
                message,
                ["error"]);

            return true;
        }
        else {
            return false;
        }
    }

    return module;
})();
