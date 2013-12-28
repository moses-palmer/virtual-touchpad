exports.messages = (function() {
    var module = {};

    /**
     * Inserts error messages into the list el, or deletes el if not error
     * messages exist.
     *
     * @param el
     *     The element to hold the error messages. This element must be able to
     *     parent li elements. This element is removed if no error messages
     *     exist.
     * @return the number of errors inserted; 0 if el was removed
     */
    module.insertErrors = function(el) {
        var list = document.createDocumentFragment();

        /**
         * Inserts an error message.
         *
         * @param message
         *     The error message.
         */
        function insertError(message) {
            var li = document.createElement("li");
            li.innerText = message;
            list.appendChild(li);
        }

        var result = 0;

        // We need WebSocket support to even send messages to the server
        if (checks.failed("WebSocket")) {
            insertError(
                "WebSockets are not supported");
            result++;
        }

        // We need touch events to simulate touchpad
        if (checks.failed("TouchEvents")) {
            insertError(
                "Touch events are not supported");
            result++;
        }

        // If any checks failed, add them to the displayed list, otherwise
        // remove the list
        if (list.childNodes.length > 0) {
            el.appendChild(list);
        }
        else {
            el.parentElement.removeChild(el);
        }

        return result;
    }

    return module;
})();

