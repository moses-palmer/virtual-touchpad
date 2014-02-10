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
     * @param value
     *     The current value of the Trackbar.
     * @param minValue, maxValue
     *     The minimum and maximum value of the Trackbar
     */
    var Trackbar = function(parentEl, value, minValue, maxValue) {
        this.parentEl = parentEl;
        this._value =
            value < minValue
                ? minValue
                : value > maxValue
                    ? maxValue
                    : value;
        this.minValue = minValue;
        this.maxValue = maxValue;

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

    /**
     * Repositions the mark element to reflect the current value.
     */
    Trackbar.prototype._refresh = function() {
        var maxLeft = this.parentEl.clientWidth - this.markEl.clientWidth;
        this.markEl.style.left = (maxLeft
            * (this._value - this.minValue) / (this.maxValue - this.minValue))
                .toFixed(0) + "px";
    };

    return module;
})();

