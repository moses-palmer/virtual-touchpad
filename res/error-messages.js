(function() {
    var errorMessages = document.getElementById("error-messages");
    var errorList = document.createDocumentFragment();

    /**
     * Inserts an error message.
     *
     * @param message
     *     The error message.
     */
    function insertError(message) {
        var li = document.createElement("li");
        li.innerText = message;
        errorList.appendChild(li);
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

    // If any checks failed, add them to the displayed list, otherwise remove
    // the list
    if (errorList.childNodes.length > 0) {
        errorMessages.appendChild(errorList);
    }
    else {
        errorMessages.parentElement.removeChild(errorMessages);
    }
})();
