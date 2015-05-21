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
exports.keyboard = (function() {
    var module = {
        EL: "keyboard",

        /**
         * The class used to mark the root element that contains all keys.
         */
        KEYS_ROOT_CLASS: "keys",

        /**
         * The class used to mark each key element.
         */
        KEY_CLASS: "key",

        /**
         * The attribute of a key element that contains its symbol name.
         */
        SYMBOL_ATTR: "x-symbol",

        /**
         * The attribute of a key element that contains its symbol identifier.
         */
        KEYSYM_ATTR: "x-keysym",

        /**
         * The attribute of a key element that contains its keyboard row.
         *
         * This attribute is used to look up keys without SYMBOL_ATTR set.
         */
        ROW_ATTR: "x-row",

        /**
         * The attribute of a key element that contains its keyboard column.
         *
         * This attribute is used to look up keys without SYMBOL_ATTR set.
         */
        COL_ATTR: "x-col",

        /**
         * Gets the value of a modifier by reading the class list of an element.
         *
         * @param el
         *     The keyboard element.
         * @param name
         *     The modifier name. This should be one of the constants in
         *     module.MOD_CLASSES.
         * @return whether the modifier is set on the element
         */
        getModifier: function(el, name) {
            return el.classList.contains(name)
                || el.classList.contains(module.MOD_CLASSES.BOTH);
        },

        /**
         * Sets a modifier for an element by modifying the class list.
         *
         * @param el
         *     The keyboard element.
         * @param name
         *     The modifier name. This should be one of the constants in
         *     module.MOD_CLASSES.
         * @param value
         *     Whether to set or clear the modifier.
         */
        setModifier: function(el, name, value) {
            var other;
            switch(name) {
            case module.MOD_CLASSES.SHIFT:
                other = module.MOD_CLASSES.ALTGR;
                break;
            case module.MOD_CLASSES.ALTGR:
                other = module.MOD_CLASSES.SHIFT;
                break;
            default:
                return;
            }

            if (value) {
                if (module.getModifier(el, other)) {
                    el.classList.remove(other);
                    el.classList.add(module.MOD_CLASSES.BOTH);
                }
                else {
                    el.classList.add(name);
                }
                el.classList.remove(module.MOD_CLASSES.NONE);
            }
            else {
                if (el.classList.contains(module.MOD_CLASSES.BOTH)) {
                    el.classList.remove(module.MOD_CLASSES.BOTH);
                    el.classList.add(other);
                }
                else {
                    el.classList.remove(name);
                    el.classList.add(module.MOD_CLASSES.NONE);
                }
            }
        },

        /**
         * The classes used to set the state of the modifiers on the parent
         * element.
         */
        MOD_CLASSES: {
            /** No modifier is active */
            NONE: "mod-none",

            /** Both shift and altgr is active */
            BOTH: "mod-both",

            /** Only shift is active */
            SHIFT: "mod-shift",

            /** Only altgr is active */
            ALTGR: "mod-altgr"
        },

        READY_CLASS: "ready"
    };

    /**
     * The keyboard.
     */
    function Keyboard(parentEl, src, layout) {
        this.parentEl = parentEl;
        this.doc = null;
        this._touches = {};

        // Initially, no modifier is toggled
        parentEl.classList.add(module.MOD_CLASSES.NONE);
        Object.defineProperty(this, "shift", {
            get: function() {
                return module.getModifier(parentEl, module.MOD_CLASSES.SHIFT);
            },
            set: function(value) {
                module.setModifier(parentEl, module.MOD_CLASSES.SHIFT, value);
            }
        });
        Object.defineProperty(this, "altgr", {
            get: function() {
                return module.getModifier(parentEl, module.MOD_CLASSES.ALTGR);
            },
            set: function(value) {
                module.setModifier(parentEl, module.MOD_CLASSES.ALTGR, value);
            }
        });

        // Allow actually setting the layout
        this._layout = layout
        Object.defineProperty(this, "layout", {
            get: function() {
                return this._layout;
            },
            set: function(value) {
                this._layout = value;

                // Make sure to mark the keyboard as non-ready
                parentEl.classList.remove(module.READY_CLASS);

                // Get the layout
                var ajax = new XMLHttpRequest();
                ajax.open("GET", value, true);
                ajax.send();
                ajax.onload = (function(e) {
                    try {
                        // Apply the layout and mark the keyboard as ready
                        if (this._applyLayout(JSON.parse(ajax.responseText))) {
                            parentEl.classList.add(module.READY_CLASS);
                        }
                        else {
                            // TODO: Handle
                        }
                    }
                    catch (e) {
                        // TODO: Handle
                    }
                }).bind(this);
            }
        });

        // Get the keyboard SVG
        var ajax = new XMLHttpRequest();
        ajax.open("GET", src, true);
        ajax.send();
        ajax.onload = (function(e) {
            // First parse the data into an SVG document
            var parser = new DOMParser();
            var doc = parser.parseFromString(ajax.responseText, "text/xml");

            // Insert the document into the DOM and get a reference to it
            parentEl.appendChild(doc.documentElement);
            this.svg = parentEl.querySelector("svg");

            // Get the element that contains all keys
            this.keys = this.svg.querySelector("." + module.KEYS_ROOT_CLASS);

            // Attach touch event handlers
            this.keys.addEventListener("touchstart",
                this.onTouchStart.bind(this));
            this.keys.addEventListener("touchmove",
                this.onTouchMove.bind(this));
            this.keys.addEventListener("touchend",
                this.onTouchEnd.bind(this));

            // Apply the layout now if specified; the keyboard will be marked as
            // ready once it has been loaded and applied
            if (layout) {
                this.layout = layout;
            }
            else {
                parentEl.classList.add(module.READY_CLASS);
            }
        }).bind(this);
    };
    module.Keyboard = Keyboard;

    /**
     * Determines whether a DOM element represents a key.
     *
     * An element is considered as a key if its immediate parent is the element
     * with the ID module.KEYS_ROOT_ELEMENT.
     *
     * @param el
     *     The DOM element to check.
     * @return whether the element is a key
     */
    Keyboard.prototype._isKey = function isKey(el) {
        // All keys are part of the "keys" group
        return el.classList && el.classList.contains(module.KEY_CLASS);
    };

    /**
     * Retrieves the key at the specified position.
     *
     * @param row
     *     The row of the key.
     * @param col
     *     The column of the key.
     * @return the key element if it exists
     */
    Keyboard.prototype._getKey = function getKey(row, col) {
        return this.svg.querySelector("." + module.KEY_CLASS
            + "[" + module.ROW_ATTR + "='" + row + "']"
            + "[" + module.COL_ATTR + "='" + col + "']");
    };

    /**
     * Returns the row to which a key belongs.
     *
     * @param key
     *     The key DOM element.
     * @return the row, or NaN if it cannot be determined
     */
    Keyboard.prototype._getRow = function getRow(key) {
        return parseInt(key.getAttribute(module.ROW_ATTR));
    };

    /**
     * Returns the column to which a key belongs.
     *
     * @param key
     *     The key DOM element.
     * @return the column, or NaN if it cannot be determined
     */
    Keyboard.prototype._getCol = function getCol(key) {
        return parseInt(key.getAttribute(module.COL_ATTR));
    };

    /**
     * Calls callback for every key that is touched by on of the touches in
     * touches.
     *
     * @param touches
     *     A list of Touch instances.
     * @param callback
     *     The callback to call for each touch that is located over a key. This
     *     callback will be passed the parameters key, which is the key element,
     *     and touchID, which is the identifier of the Touch instance. If the
     *     touch does not hover above a key, null will be passed as key.
     */
    Keyboard.prototype._eachKey = function eachKey(touches, callback) {
        for (var i = 0; i < touches.length; i++) {
            var touch = touches[i];
            var el = document.elementFromPoint(touch.pageX, touch.pageY);
            while (el) {
                if (this._isKey(el)) {
                    break;
                }
                el = el.parentNode;
            }

            callback(el, touch.identifier);
        }
    };

    /**
     * Adds text elements to an SVG elements from a layout key array.
     *
     * The text elements will have the correct classes applied.
     *
     * @param el
     *     The parent element. This element must contain at least one child
     *     element, which is used to center the text elements.
     * @param key
     *     A key from the layout. See the layout README for a description of the
     *     format.
     */
    Keyboard.prototype._addTexts = function addTexts(el, key) {
        for (var i  =0; i < key.length; i++) {
            var name = key[i][0];
            if (!name) {
                continue;
            }
            var shift = (i & 1) != 0;
            var altgr = (i & 2) != 0;
            var x = parseInt(el.firstChild.getAttribute("x"));
            var y = parseInt(el.firstChild.getAttribute("y"));

            var text = document.createElementNS("http://www.w3.org/2000/svg",
                "text");
            text.appendChild(document.createTextNode(name));
            if (shift && altgr) {
                text.classList.add(module.MOD_CLASSES.BOTH);
            }
            else if (shift) {
                text.classList.add(module.MOD_CLASSES.SHIFT);
            }
            else if (altgr) {
                text.classList.add(module.MOD_CLASSES.ALTGR);
            }
            else {
                text.classList.add(module.MOD_CLASSES.NONE);
            }

            // TODO: Solve this better
            text.setAttribute("text-anchor", "middle");
            text.setAttribute("x", x + 13);
            text.setAttribute("y", y + 18);

            el.appendChild(text);
        }
    };

    /**
     * Applies a keyboard layout.
     *
     * All keyboard keys described in the layout will have their text labels
     * updated.
     *
     * If the layout is incorrect, the state of the keyboard is undefined.
     *
     * @param layout
     *     The layout data. See the layout README for a description of the
     *     format.
     * @return whether the layout was applied correctly
     */
    Keyboard.prototype._applyLayout = function applyLayout(layout) {
        // Iterate over all keys
        for (var row = 0; row < layout.layout.length; row++) {
            var rowData = layout.layout[row];
            for (var col = 0; col < rowData.length; col++) {
                var keyData = rowData[col];

                // Get the actual key element
                var key = this._getKey(row, col);
                if (!key) {
                    return false;
                }

                // Remove all child nodes except for the first one
                while (key.childkeyementCount > 1) {
                    key.removeChild(key.childNodes[1]);
                }

                // Add new nodes
                this._addTexts(key, keyData);
            }
        }

        this._layoutData = layout;

        return true;
    };

    Keyboard.prototype.onTouchStart = function onTouchStart(t) {
        this._eachKey(t.touches, (function(key, touchID) {
            this._touches[touchID] = key;
            if (key) {
                this._press(key);
            }
        }).bind(this));

        t.preventDefault();
    };

    Keyboard.prototype.onTouchMove = function onTouchMove(t) {
        this._eachKey(t.touches, (function(key, touchID) {
            // If a touch hovers above a new key, release the old key
            var previousKey = this._touches[touchID];
            if (previousKey && previousKey !== key) {
                this._release(previousKey);
            }
            if (key && key !== previousKey) {
                this._touches[touchID] = key;
                this._press(key);
            }
        }).bind(this));

        t.preventDefault();
    };

    Keyboard.prototype.onTouchEnd = function onTouchEnd(t) {
        this._eachKey(t.changedTouches, (function(key, touchID) {
            var previousKey = this._touches[touchID];
            this._release(previousKey);
            delete this._touches[touchID];
        }).bind(this));

        t.preventDefault();
    };

    /**
     * Handles pressing and releasing of a key.
     *
     * This method will update the class list of the key element, update the
     * modifier state and emit the "press" or "release" event.
     *
     * @param key
     *     The key element being pressed or released.
     * @param pressed
     *     Whether the key is being pressed.
     */
    Keyboard.prototype._handleKey = function handleKey(key, pressed) {
        // Update the key class
        if (pressed) {
            key.classList.add("pressed");
        }
        else {
            key.classList.remove("pressed");
        }

        // Get the key symbol
        var name = null;
        var keysym = key.getAttribute(module.KEYSYM_ATTR);
        var symbol = key.getAttribute(module.SYMBOL_ATTR);

        // If the geometry file does not contain the key symbol, we need to look
        // it up in the layout
        if (!symbol) {
            var row = this._getRow(key);
            var col = this._getCol(key);
            var key = this._layoutData.layout[row][col];
            var index = (this.shift << 0) | (this.altgr << 1);
            name = key[index][0];
            keysym = key[index][1];
            symbol = key[index][2];
        }

        switch (symbol) {
        case "ISO_Level3_Shift":
            this.altgr = pressed;
            break;

        case "Caps_Lock":
            if (pressed) {
                this.shift = !this.shift;
            }
            break;

        case "Shift_L":
        case "Shift_R":
            this.shift = pressed;
            break;
        }

        this.parentEl.dispatchEvent(new CustomEvent(
            pressed ? "press" : "release",
            {"detail": [name, keysym, symbol]}));
    };

    /**
     * Handles pressing of a key.
     *
     * This will cause the parent element to dispatch the "press" event, and if
     * the key is a toggle key, the keys to update accordingly.
     *
     * @param key
     *     The key element.
     */
    Keyboard.prototype._press = function press(key) {
        // TODO: Allow configuration
        if (navigator.vibrate) {
            navigator.vibrate(20);
        }

        this._handleKey(key, true);
    };

    /**
     * Handles releasing of a key.
     *
     * This will cause the parent element to dispatch the "release" event, and
     * if the key is a toggle key, the keys to update accordingly.
     *
     * @param key
     *     The key element.
     */
    Keyboard.prototype._release = function release(key) {
        this._handleKey(key, false);
    };

    /**
     * Automatically instantiate all keyboards when the document is loaded.
     */
    addEventListener("load", function() {
        var els = document.querySelectorAll(module.EL);

        for (var i = 0; i < els.length; i++) {
            var el = els[i];

            var src = el.getAttribute("src");
            var layout = el.getAttribute("layout");

            el.keyboard = new Keyboard(el, src, layout);

            // Automatically attach the event handlers
            var onpress = el.getAttribute("onpress");
            if (onpress) {
                el.addEventListener("press", function(event) {
                    eval(onpress);
                })
            }
            var onrelease = el.getAttribute("onrelease");
            if (onrelease) {
                el.addEventListener("release", function(event) {
                    eval(onrelease);
                })
            }
        }
    });

    return module;
})();
