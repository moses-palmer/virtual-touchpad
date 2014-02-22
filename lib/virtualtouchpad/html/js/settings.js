exports.settings = (function() {
    var overlay, view;
    var module = {
        show: function() {
            overlay.style.display = "block";
        },

        hide: function() {
            overlay.style.display = "none";
        }};

    /**
     * Locate the overlay element.
     */
    exports.onloadCallbacks.push(function() {
        overlay = document.getElementById("settings-overlay");
        overlay.onclick = module.hide;

        view = document.getElementById("settings-view");
        view.addEventListener("touchstart", function(e) {
            e.preventDefault();
        });
    });

    return module;
})();
