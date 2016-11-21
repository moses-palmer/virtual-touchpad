"use strict";

var system = require('system');


function error(message) {
    system.stderr.write("ERROR: " + message + "\n");
    system.stderr.flush();
}


/**
 * The main function.
 *
 * This function will read a line from `stdin` and parse it as a JSON directive.
 *
 * The value of `command` will be used as command, and corresponds to an entry
 * in `HANDLERS`, and the value of `args` will be passed as arguments to the
 * handler.
 */
function main() {
    var directive = JSON.parse(system.stdin.readLine());

    try {
        HANDLERS[directive.command](
            directive.args,
            function(e) {
                if (e) {
                    error(e);
                    phantom.exit(1);
                }
                else {
                    phantom.exit(0);
                }
            });
    }
    catch (e) {
        error(e);
    }
}


/**
 * Opens a page.
 *
 * @param complete A callback to call when the handler and its spawned tasks
 *     have completed.
 * @param callback The callback to call on success. It will be passed the page
 *     as its only parameter.
 * @param args Any arguments.
 * @throws if the page cannot be opened
 */
function withPage(callback, args, complete) {
    var page = require("webpage").create();
    page.open(
        args.source,

        function(status) {
            if (status !== "success") {
                complete("unable to load file " + args.source);
            }
            else {
                try {
                    callback(complete, page, args);
                }
                catch (e) {
                    complete(e);
                }
            }
        });
}


/**
 * Extracts the dimensions from the page document element.
 *
 * @param page The page.
 * @return a map with the attributes `width` and `height`
 */
function dimensions(page) {
    return page.evaluate(function() {
        var el = document.documentElement;

        return {
            width: el.width.animVal.value,
            height: el.height.animVal.value};
    });
}


var HANDLERS = {
    convert: withPage.bind(null, function(complete, page, args) {
        setTimeout(
            function() {
                var dim = dimensions(page);
                var xscale = (1.0 * args.size) / dim.width;
                var yscale = (1.0 * args.size) / dim.height;
                page.viewportSize = {
                    width: dim.width * xscale,
                    height: dim.height * yscale};
                page.clipRect = {
                    width: dim.width * xscale,
                    height: dim.height * yscale};
                page.zoomFactor = xscale;

                try {
                    page.render(
                        args.target,
                        {
                            format : "png"});
                    complete();
                }
                catch (e) {
                    complete(e);
                }
            },
            0);
    })
};


main();
