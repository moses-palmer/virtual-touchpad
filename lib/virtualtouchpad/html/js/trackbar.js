exports.trackbar = (function() {
    var module = {
        /**
         * The class of the mark element of a trackbar.
         */
        MARK_CLASS: "trackbar-mark"};

    /**
     * The trackbar.
     *
     * @param parentEl
     *     The trackbar element.
     */
    var Trackbar = function(parentEl) {
        this.parentEl = parentEl;

        // Find or create the track element
        for (var i = 0; i < parentEl.childElementCount; i++) {
            var markEl = parentEl.children[i];
            if (markEl.classList.contains(module.MARK_CLASS)) {
                this.markEl = markEl;
                break;
            }
        }
        if (!this.markEl) {
            this.markEl = document.createElement("div");
            this.markEl.className = module.MARK_CLASS;
            this.parentEl.appendChild(this.markEl);
        }
    };
    module.Trackbar = Trackbar;

    return module;
})();

