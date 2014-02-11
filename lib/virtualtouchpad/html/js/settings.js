exports.settings = (function() {
    var overlay, view;
    var module = {
        show: function() {
            overlay.style.display = "block";
        },

        hide: function() {
            overlay.style.display = "none";
        }};

    return module;
})();

