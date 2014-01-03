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
            insertError(
                "WebSockets are not supported");
        }

        // We need touch events to simulate touchpad
        if (checks.failed("TouchEvents")) {
            insertError(
                "Touch events are not supported");
        }

        // If any checks failed, add them to the displayed list
        if (list.childNodes.length > 0) {
            var message = document.createDocumentFragment();
            message.appendChild(document.createTextNode(
                "Your browser does not support Virtual Touchpad. These "
                + "features are missing:"));
            var ul = document.createElement("ul");
            ul.appendChild(list);
            message.appendChild(ul);
            message.appendChild(document.createTextNode(
                "Please upgrade your browser to a newer version."));

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

