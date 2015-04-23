/******************************************************************************/
/* virtual-touchpad                                                           */
/* Copyright (C) 2013-2015 Moses Palmér                                       */
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
exports.app = (function() {
    // Do nothing if a critical error occurred
    if (features.listMissing()) {
        return;
    }

    var module = {};

    // Automatically refresh when the AppCache is changed
    if (window.applicationCache) {
        applicationCache.addEventListener("updateready",
            function(e) {
                if (applicationCache.status == applicationCache.UPDATEREADY) {
                    document.location.reload();
                }
            }, false);
    }

    var ws;
    var touchpad, touchview;
    var touchviewEl;
    module.ws = {
        onOpen: function() {
            touchpad = new controller.Touchpad(ws);
            touchview = new view.Touchview(touchviewEl, touchpad);

            // We are now connected
            document.body.classList.add("connected");
        },

        onClose: function() {
            touchview.detach();
            touchpad = undefined;

            // This happens when the server closes the connection
            messagebox.show(_(
                // <a href=...> and </a> must not be translated
                "Connection closed. Please click "
                + "<a href='javascript:location.reload();'>here</a> to "
                + "reconnect."),
                ["error"]);

            // We are now disconnected
            document.body.classList.remove("connected");
        },

        onError: function(error) {
            messagebox.show(_(
                // Do not translate <host>
                "Failed to connect. Please verify that <host> is running.")
                    .replace(/<host>/g, document.location.host),
                ["error"]);

            // We are now disconnected
            document.body.classList.remove("connected");
        },

        onMessage: function(message) {
            var reason, data, tb, content, header, stack;
            try {
                var json = JSON.parse(message.data);
                reason = json.reason;
                data = "<exception> (<data>), <reason>"
                    .replace(/<exception>/g, json.exception)
                    .replace(/<data>/g, json.data.trim())
                    .replace(/<reason>/g, reason);
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
                    "Failed to send command: <code><message></code>.")
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
                caption.appendChild(
                    document.createTextNode(_("Stack trace")));
                caption.addEventListener("click", function() {
                    stack.classList.toggle("collapsed");
                });
                stack.appendChild(caption);

                // Add the stack trace
                for (var i = 0; i < tb.length; i++) {
                    start(stack);
                    add(tb[i][0]
                        .substring(tb[i][0].indexOf("virtualtouchpad")));
                    add(tb[i][1]);
                    add(tb[i][2]);
                    add(tb[i][3]);
                }

                content.appendChild(stack);
            }

            messagebox.show(content, ["error"]);
        }
    };

    /**
     * Open the WebSocket connection.
     */
    exports.onloadCallbacks.push(function() {
        touchviewEl = document.getElementById("touchpad")

        // Connect to the WebSocket
        ws = new WebSocket("ws://" + document.location.host + "/ws");
        ws.onopen = app.ws.onOpen;
        ws.onclose = app.ws.onClose;
        ws.onerror = app.ws.onError;
        ws.onmessage = app.ws.onMessage;
    });


    module.toolbar = {
        onHelp: function() {
            if (document.location.pathname.indexOf(".min.xhtml") != -1) {
                window.open("help.min.xhtml", "_blank");
            }
            else {
                window.open("help.xhtml", "_blank");
            }
        },

        onSettings: function() {
            if (!app.settings.visible()) {
                app.settings.show();
            }
            else {
                app.settings.hide();
            }
        },

        onFullscreenOn: function() {
            document.documentElement.requestFullscreen();
        }
    };

    /**
     * Remove the toolbar if SVGs are not supported.
     */
    exports.onloadCallbacks.push(function() {
        if (checks.failed("SVG")) {
            var toolbar = document.querySelector("#toolbar");
            toolbar.parentElement.removeChild(toolbar);
            return;
        }
    });


    var settingsOverlay, settingsView;
    module.settings = {
        /**
         * The name of the class added to the settings view and overlay when
         * it should be shown.
         */
        TOGGLED_CLASS: "toggled",

        /**
         * The name of the class added to the settings view and overlay when
         * it is sliding.
         */
        SLIDING_CLASS: "sliding",

        show: function() {
            settingsOverlay.classList.add(app.settings.TOGGLED_CLASS);
            settingsView.classList.add(app.settings.TOGGLED_CLASS);
        },

        visible: function() {
            return settingsView.classList.contains(
                app.settings.TOGGLED_CLASS);
        },

        slideBegin: function() {
            settingsView.classList.add(
                app.settings.SLIDING_CLASS);
        },

        slideEnd: function() {
            settingsView.classList.remove(
                app.settings.SLIDING_CLASS);
        },

        hide: function() {
            settingsOverlay.classList.remove(
                app.settings.TOGGLED_CLASS);
            settingsView.classList.remove(
                app.settings.TOGGLED_CLASS);
        }
    };

    /**
     * Initialise the settings view and overlay.
     */
    exports.onloadCallbacks.push(function() {
        var firstTouch, currentTouch;
        var i = 0;

        function dx(touch) {
            return touch.screenX - firstTouch.screenX;
        }

        settingsOverlay = document.getElementById("settings-overlay");
        settingsOverlay.addEventListener("touchstart", function(event) {
            app.settings.slideBegin();

            // Make sure we have a description of the first touch
            firstTouch = util.cloneTouches(event.touches)[0];
        });
        settingsOverlay.addEventListener("touchmove", function(event) {
            // Find the new incarnation of the original touch
            var c = event.changedTouches.identifiedTouch(
                firstTouch.identifier);
            if (!c) {
                return;
            }
            currentTouch = c;

            // Slide the view, and make sure to snap it to the edge
            var d = dx(currentTouch).toFixed(0);
            if (d > 0) d = 0;
            settingsView.style.marginLeft = d + "px";
        });
        settingsOverlay.addEventListener("touchend", function(e) {
            var d = dx(currentTouch) / settingsView.clientWidth;
            if (d < -0.15) {
                app.settings.hide();
            }
            else if (d > 0.5) {
                app.settings.show();
            }
            else {
                if (app.settings.visible()) {
                    app.settings.show();
                }
                else {
                    app.settings.hide();
                }
            }

            // Make sure to remove the explicitly set style to allow the CSS to
            // decide
            settingsView.removeAttribute("style");

            app.settings.slideEnd();
        });

        settingsView = document.getElementById("settings-view");
        settingsView.addEventListener("touchstart", function(e) {
            e.preventDefault();
        });
    });


    return module;
})();
