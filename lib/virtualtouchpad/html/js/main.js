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

        // We are now connected
        document.body.classList.add("connected");
    }

    ws.onclose = function() {
        touchview.detach();
        touchpad = undefined;

        // This happens when the server closes the connection
        messagebox.show(_(
            // <a href=...> and </a> must not be translated
            "Connection closed. Please click "
            + "<a href='javascript:location.reload();'>here</a> to reconnect."),
            ["error"]);

        // We are now disconnected
        document.body.classList.remove("connected");
    }

    ws.onerror = function(error) {
        messagebox.show(_(
            // Do not translate <host>
            "Failed to connect. Please verify that <host> is running.")
                .replace(/<host>/g, document.location.host),
            ["error"]);

        // We are now disconnected
        document.body.classList.remove("connected");
    };

    ws.onmessage = function(message) {
        var reason, data, tb, content, header, stack;
        try {
            var json = JSON.parse(message.data);
            reason = json.reason;
            data = json.exception + "(" + json.data.trim() + "), " + reason;
            tb = json.tb;
        }
        catch (e) {
            reason = "unknown";
            data = message.data;
        }

        content = document.createElement("div");
        switch (reason) {
        case "invalid_command":
        case "invalid_data":
            header = _(
                // Do not translate <host> or <message>
                "Failed to send command to <host>: <code><message></code>.")
                    .replace(/<host>/g, document.location.host)
                    .replace(/<message>/g, data.xmlEscape());
            break;

        case "internal_error":
            header = _(
                // Do not translate <host> or <message>
                "An error occurred on <host>: <code><message></code>.")
                    .replace(/<host>/g, document.location.host)
                    .replace(/<message>/g, data.xmlEscape());
            break;

        default:
            header = _(
                // Do not translate <host> or <message>
                "An unknown error occurred: <code><message></code>.")
                    .replace(/<message>/g, data.xmlEscape());
            break;
        }
        content.innerHTML = header;

        if (tb) {
            var row;
            function start(targetEl) {
                row = document.createElement("tr");
                targetEl.appendChild(row);
            }
            function add(text) {
                var td = document.createElement("td");
                td.appendChild(document.createTextNode(text));
                row.appendChild(td);
            }
            stack = document.createElement("table");
            stack.classList.add("stack");
            stack.classList.add("collapsed");

            // Add a caption to the table
            var caption = document.createElement("caption");
            caption.appendChild(document.createTextNode(_("Stack trace")));
            caption.addEventListener("click", function() {
                stack.classList.toggle("collapsed");
            });
            stack.appendChild(caption);

            // Add the stack trace
            for (var i = 0; i < tb.length; i++) {
                start(stack);
                add(tb[i][0].substring(tb[i][0].indexOf("virtualtouchpad")));
                add(tb[i][1]);
                add(tb[i][2]);
                add(tb[i][3]);
            }

            content.appendChild(stack);
        }

        messagebox.show(content, ["error"]);
    };
});
