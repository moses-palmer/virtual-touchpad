// Make sure exports work
exports = window;

// Keep all 'window.onload' functions in this array
exports.onloadCallbacks = [];
window.onload = function() {
    for (var i = 0; i < exports.onloadCallbacks.length; i++) {
        exports.onloadCallbacks[i]();
    }
};

