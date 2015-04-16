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
exports.toolbar = (function() {
    /**
     * Updates toolbar buttons to reflect the current fullscreen mode.
     */
    function fullscreenUpdate() {
        document.querySelector("#toolbar > .fullscreen.on"
            ).style.display =
                (document[document.FULLSCREEN_ELEMENT_NAME]
                        || checks.failed("Fullscreen"))
                    ? "none"
                    : "table-cell";
    }

    /**
     * Remove the bottom toolbar if SVGs are not supported, otherwise update the
     * fullscreen buttons.
     */
    exports.onloadCallbacks.push(function() {
        var bottomToolbar = document.querySelectorAll("#toolbar")[0];

        // Remove the toolbar element if SVGs are not supported
        if (checks.failed("SVG")) {
            bottomToolbar.parentElement.removeChild(bottomToolbar);
            return;
        }

        fullscreenUpdate();
        document.addEventListener(
            document.FULLSCREENCHANGE_EVENT_NAME,
            fullscreenUpdate);
    });

    return {
        onHelp: function() {
            if (document.location.pathname.indexOf(".min.xhtml") != -1) {
                window.open("help.min.xhtml", "_blank");
            }
            else {
                window.open("help.xhtml", "_blank");
            }
        },

        onSettings: function() {
            if (!settings.visible()) {
                settings.show();
            }
            else {
                settings.hide();
            }
        },

        onFullscreenOn: function() {
            document.documentElement.requestFullscreen();
        }
    };
})();
