import os
import sys


def create(source_path, target_path, dimensions):
    """
    Creates a PNG image from an SVG image and scales it.

    @param source_path
        The SVG source.
    @param target_path
        The output target.
    @param scale
        The scale at which to render the target. Specify 1 to keep the size of
        the original.
    """
    try:
        import cairo
        from gi.repository import Rsvg as rsvg
    except ImportError as e:
        sys.stdout.write('Import failed: %s; %s will not be generated.' % (
            e.args[0], target_path) + '\n')
        return

    rwidth, rheight = dimensions

    # Load the SVG file
    handle = rsvg.Handle()
    svg = handle.new_from_file(source_path)

    # Create the surface and context
    dim = svg.get_dimensions()
    iwidth, iheight = dim.width, dim.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
        rwidth,
        rheight)
    context = cairo.Context(surface)

    # Render the icon at the correct scale
    context.scale(1.0 * rwidth / iwidth, 1.0 * rheight / iheight)
    svg.render_cairo(context)

    # Save the file
    surface.write_to_png(target_path)


def app_icon(size, target_path):
    """
    Creates an application icon PNG.

    @param size
        The required size of the output.
    @param target
        The output target.
    """
    # Create a PNG image from ./res/icon; its size is 16 px
    create(
        os.path.join(
            os.path.dirname(__file__),
            'res',
            'icon.svg'),
        target_path,
        (size, size))
