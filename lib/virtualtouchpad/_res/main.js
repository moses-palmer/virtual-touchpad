exports.main = function() {
    // Do nothing if a critical error occurred
    if (features.listMissing()) {
        return;
    }

    var touchpad, touchview;
    var touchviewEl = document.getElementById("touchpad");

    // Connect to the WebSocket
    ws = new WebSocket("ws://" + document.location.host + "/ws");

    ws.onopen = function() {
        touchpad = new controller.Touchpad(ws);
        touchview = new view.Touchview(touchviewEl, touchpad);
    }

    ws.onclose = function() {
        touchview.detach();
        touchpad = undefined;

        // This happens when the server closes the connection
        messagebox.show(
            "Connection closed. Please click "
            + "<a href='javascript:location.reload();'>here</a> to reconnect.",
            ["error"]);
    }

    ws.onerror = function(error) {
        // This is probably caused by offline use
        messagebox.show(
            "Failed to connect. Please verify that <host> is running."
                .replace(/<host>/g, document.location.host),
            ["error"]);
    };
};

