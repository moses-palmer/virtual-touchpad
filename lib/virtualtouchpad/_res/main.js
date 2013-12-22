exports.main = function() {
    if (checks.failures.length > 0) {
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
};
