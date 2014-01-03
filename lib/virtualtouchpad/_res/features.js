exports.features = (function() {
    var module = {};

    /**
     * Inserts missing features into the list el, or deletes el if no required
     * features are missing.
     *
     * @param el
     *     The element to hold the list. This element must be able to parent li
     *     elements. This element is removed if no missing features exist.
     * @return the number of errors inserted; 0 if el was removed
     */
    module.listMissing = function(el) {
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

        // If any checks failed, add them to the displayed list, otherwise
        // remove the list
        if (list.childNodes.length > 0) {
            el.appendChild(list);
        }
        else {
            el.parentElement.removeChild(el);
        }

        return checks.failures.length;
    }

    return module;
})();

