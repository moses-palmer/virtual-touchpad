exports.messagebox = (function() {
    var module = {};

    /**
     * Displays the message box.
     *
     * @param message
     *     The message to display. This may be either a string, which will be
     *     displayed verbatim, or an element, which will be set as the child o
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
        mbox.style.display = "block";
    };

    return module;
})();
