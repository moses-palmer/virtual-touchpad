exports.main = function() {
    // Do nothing if a critical error occurred
    if (features.listMissing(document.getElementById("missing-features")) > 0) {
        return;
    }

    var touchpad, touchview;
    var touchviewEl = document.getElementById("touchpad");

    // Connect to the WebSocket
    ws = new WebSocket("ws://" + document.location.host + "/ws");

    ws.onopen = function() {
        touchpad = new controller.Touchpad(ws);
        touchview = new view.Touchview(touchviewEl, touchpad);
        touchviewEl.style.display = "block";
    }

    ws.onclose = function() {
        touchpad = undefined;
        touchviewEl.style.display = "none";
    }

    ws.onerror = function(error) {
        // This is probably caused by offline use
        var offlineEl = document.getElementById("error-message");
        offlineEl.innerText = (
            "Failed to connect. Please verify that <host> is running.")
                .replace(/<host>/g, document.location.host);
        offlineEl.classList.add("error");
    };
};

