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

    // TODO: Add failed tests to errorList


    // If any checks failed, add them to the displayed list, otherwise remove
    // the list
    if (errorList.childNodes.length > 0) {
        errorMessages.appendChild(errorList);
    }
    else {
        errorMessages.parentElement.removeChild(errorMessages);
    }
})();
