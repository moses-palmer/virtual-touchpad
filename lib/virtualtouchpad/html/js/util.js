exports.util = (function() {
    var module = {};

    /**
     * Clones an array of touches keeping only identifier, screenX, screenY,
     * clientX and clientY.
     *
     * @param touches
     *     A TouchList to clone. If this is falsy, [] is returned.
     * @return an array of objects
     */
    module.cloneTouches = function(touches) {
        if (!touches) return [];

        var result = [];

        for (var i = 0; i < touches.length; i++) {
            result.push({
                identifier: touches[i].identifier,
                screenX: touches[i].screenX,
                screenY: touches[i].screenY,
                clientX: touches[i].clientX,
                clientY: touches[i].clientY});
        }

        return result;
    };

    /**
     * Returns the position of an element, relative to the viewport.
     *
     * @return the array [x, y]
     */
    Element.prototype.position = function() {
        var x = 0;
        var y = 0;

        var o = this;
        while (true) {
            x += o.offsetLeft;
            y += o.offsetTop;
            if (o.offsetParent === null){
                break;
            }
            o = o.offsetParent;
        }

        return [x, y];
    };

    return module;
})();

