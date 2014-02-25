/******************************************************************************/
/* virtual-touchpad                                                           */
/* Copyright (C) 2013-2014 Moses Palmér                                       */
/*                                                                            */
/* This program is free software: you can redistribute it and/or modify it    */
/* under the terms of the GNU General Public License as published by the Free */
/* Software Foundation, either version 3 of the License, or (at your option)  */
/* any later version.                                                         */
/*                                                                            */
/* This program is distributed in the hope that it will be useful, but        */
/* WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY */
/* or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License    */
/* for more details.                                                          */
/*                                                                            */
/* You should have received a copy of the GNU General Public License along    */
/* with this program. If not, see <http://www.gnu.org/licenses/>.             */
/******************************************************************************/
exports.onloadCallbacks.push(function() {
    // Do nothing if a critical error occurred
    if (features.listMissing()) {
        return;
    }

    // Automatically refresh when the AppCache is changed
    if (window.applicationCache) {
        applicationCache.addEventListener("updateready",
            function(e) {
                if (applicationCache.status == applicationCache.UPDATEREADY) {
                    document.location.reload();
                }
            }, false);
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
});
