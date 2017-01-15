/*****************************************************************************/
/* virtual-touchpad                                                          */
/* Copyright (C) 2013-2017 Moses Palmér                                      */
/*                                                                           */
/* This program is free software: you can redistribute it and/or modify it   */
/* under the terms of the GNU General Public License as published by the     */
/* Free Software Foundation, either version 3 of the License, or (at your    */
/* option) any later version.                                                */
/*                                                                           */
/* This program is distributed in the hope that it will be useful, but       */
/* WITHOUT ANY WARRANTY; without even the implied warranty of                */
/* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General  */
/* Public License for more details.                                          */
/*                                                                           */
/* You should have received a copy of the GNU General Public License along   */
/* with this program. If not, see <http://www.gnu.org/licenses/>.            */
/*****************************************************************************/
/**
 * Provides access to the server status.
 *
 * The event `statusload` will be dispatched on the document element when the
 * status is available. The event `statusupdate` will be dispatched on the
 * document element when the server status is updated.
 */
exports.server = (function() {
    var module = {
        /**
         * The server status values.
         */
        status: {}
    };

    // Get the server status
    var ajax = new XMLHttpRequest();
    ajax.open("GET", "/status", true);
    ajax.send();
    ajax.onload = function(e) {
        var json = JSON.parse(ajax.responseText);
        module.status = json;
        document.dispatchEvent(
            new CustomEvent("statusload", {detail: json}));
    };

    // Continuously receive updates
    var ws = new WebSocket("ws://${host}/status/updates".format(
        util.mapSupplier(window.location)));
    ws.onmessage = function(e) {
        var json = JSON.parse(e.data);
        module.status[json.item] = json.value;
        document.dispatchEvent(
            new CustomEvent("statusupdate", {detail: json}));
    };

    return module;
})();
