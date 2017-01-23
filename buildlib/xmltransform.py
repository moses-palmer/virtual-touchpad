import os

from xml.dom import Node
from xml.dom.minidom import CDATASection

from . import LICENSE, update_file_time, HTML_ROOT

#: Elements that are allowed to be self-closing in XHTML
_VOID_ELEMENTS = [
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'keygen',
    'link', 'meta', 'param', 'source', 'track', 'wbr']


def _src_to_path(source_dir, value):
    """Converts a ``src`` attribute value to an absolute path.

    :param str source_dir: The directory in which the document that contains
        the tag is located.

    :param str value: The attribute value. If this is an absolute path, a path
        relative to :attr:`build.HTML_ROOT` is returned.

    :return: an absolute path
    """
    if value[0] == '/':
        return os.path.join(HTML_ROOT, value[1:])
    else:
        return os.path.join(source_dir, value)


def _recurse(e, callback, **kwargs):
    """Calls callback for e and its children and kwargs"""
    callback(e, **kwargs)
    for s in e.childNodes:
        _recurse(s, callback, **kwargs)


def _trim(e):
    """Trims extra whitespace of text nodes; CDATA nodes are not modified"""
    if e.nodeType == Node.TEXT_NODE:
        e.nodeValue = ' '.join(e.nodeValue.split())


def _remove_comments(e):
    """Removes comment nodes"""
    if e.nodeType == Node.COMMENT_NODE and e.parentNode:
        e.parentNode.removeChild(e).unlink()


def _clear_x_tr_values(e):
    """Clears the values of x-tr attributes"""
    if e.nodeType == Node.ELEMENT_NODE and e.hasAttribute('x-tr'):
        e.setAttribute('x-tr', '')


def _inline_script(e, source_dir, dom, files):
    """Inlines script tags"""
    # Only use script tags with src attribute
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'script' \
            or not e.hasAttribute('src') \
            or e.getAttribute('x-no-inline') == 'true':
        return

    # Read the script source and inline it
    src_path = _src_to_path(
        source_dir,
        e.getAttribute('src'))
    with open(src_path, 'rb') as src:
        cdata = CDATASection()
        cdata.replaceWholeText(src.read().decode('utf-8'))
        e.appendChild(cdata)

    # Make sure to remove the src attribute
    e.removeAttribute('src')

    files.append(src_path)


def _inline_css(e, source_dir, dom, files):
    """Inlines CSS"""
    # Only use CSS stylesheet tags
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'link' \
            or e.getAttribute('rel') != 'stylesheet' \
            or e.getAttribute('type') != 'text/css':
        return

    # Read the stylesheet and inline it
    href_path = _src_to_path(
        source_dir,
        e.getAttribute('href'))
    with open(href_path, 'rb') as href:
        cdata = CDATASection()
        cdata.replaceWholeText(href.read().decode('utf-8'))
        e.appendChild(cdata)

    # Remove all attributes except for type
    for i in range(e.attributes.length):
        attribute = e.attributes.item(i)
        if not attribute:
            continue
        if attribute.name == 'type':
            continue
        e.removeAttribute(attribute.name)

    # Change the tag name
    e.tagName = 'style'

    files.append(href_path)


def _inline_include(e, source_dir, dom, files):
    """Inlines img elements with Scalable Vector Graphics source"""
    from xml.dom.minidom import parseString

    # Only use img tags
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'x-include' \
            or not e.getAttribute('href') \
            or e.getAttribute('x-no-inline') == 'true':
        return

    # Load the XML
    href_path = _src_to_path(
        source_dir,
        e.getAttribute('href'))
    with open(href_path, 'rb') as href:
        doc = parseString(href.read().decode('utf-8'))

    # Strip space
    _recurse(doc, _trim)

    # Replace the x-include tag with inline XML
    e.parentNode.insertBefore(doc.documentElement, e)
    e.parentNode.removeChild(e)

    files.append(href_path)


def _join_elements(e):
    """Joins consecutive similar script and style elements"""
    # Only handle script and style tags
    if e.nodeType != Node.ELEMENT_NODE or e.tagName not in ('script', 'style'):
        return

    # Move next sibling's child nodes to this node while next sibling is
    # same type
    while e.nextSibling and e.nextSibling.nodeType == Node.ELEMENT_NODE \
            and e.tagName == e.nextSibling.tagName \
            and e.nextSibling.getAttribute('x-no-inline') != 'true':
        for child in e.nextSibling.childNodes:
            e.firstChild.appendData(child.wholeText)
        e.parentNode.removeChild(e.nextSibling)


def _minify_js(e):
    """Minifies the JavaScript in a script element"""
    import slimit

    # Only handle JavaScript elements
    if e.nodeType != Node.ELEMENT_NODE \
            or not e.tagName == 'script' \
            or not e.getAttribute('type') == 'text/javascript':
        return

    for c in e.childNodes:
        if c.nodeType != Node.CDATA_SECTION_NODE:
            continue
        c.replaceWholeText(slimit.minify(
            c.wholeText,
            mangle=True,
            mangle_toplevel=True))


def _minify_css(e):
    """Minifies the CSS in a style element"""
    import cssmin

    # Only handle CSS elements
    if e.nodeType != Node.ELEMENT_NODE \
            or not e.tagName == 'style' \
            or not e.getAttribute('type') == 'text/css':
        return

    for c in e.childNodes:
        if c.nodeType != Node.CDATA_SECTION_NODE:
            continue
        c.replaceWholeText(cssmin.cssmin(c.wholeText))


def _remove_self_closing(e, dom):
    """Makes sure that only void elements are self closing"""
    # Only handle non-void elements
    if e.nodeType != Node.ELEMENT_NODE or e.tagName in _VOID_ELEMENTS:
        return

    if len(e.childNodes) == 0:
        e.appendChild(dom.createTextNode(''))


def start(source_path):
    """Begins the *XML* transformation.

    :param str source_path: The path to the file which to transform.

    :return: a representation of the DOM
    """
    from xml.dom.minidom import parse

    return (source_path, parse(source_path), [])


def end(context, target_path):
    """Ends the *XML* transformation and writes the result.

    :param context: The *DOM* context as returned by :func:`start`.

    :param str target_path: The output file.
    """
    global LICENSE
    source_path, dom, files = context
    with open(target_path, 'wb') as target:
        target.write(dom.toxml(encoding='utf-8'))

    update_file_time(target_path, *files)


def minify_html(context):
    """ Minifies an *HTML* file.

    :param context: The *DOM* context as returned by :func:`start`.
    """
    source_path, dom, files = context

    # Trim text nodes
    _recurse(dom.documentElement, _trim)

    # Remove comments
    _recurse(dom.documentElement, _remove_comments)

    # Clear x-tr attribute values
    _recurse(dom.documentElement, _clear_x_tr_values)

    # Inline script tags
    _recurse(
        dom.documentElement,
        _inline_script,
        source_dir=os.path.dirname(source_path),
        dom=dom,
        files=files)

    # Inline CSS tags
    _recurse(
        dom.documentElement,
        _inline_css,
        source_dir=os.path.dirname(source_path),
        dom=dom,
        files=files)

    # Normalise the XML
    _recurse(
        dom.documentElement,
        lambda e: e.normalize())

    # Join similar elements
    _recurse(
        dom.documentElement,
        _join_elements)

    # Minify JavaScript
    _recurse(
        dom.documentElement,
        _minify_js)

    # Minify CSS
    _recurse(
        dom.documentElement,
        _minify_css)

    # Make sure only void elements are self-closing
    _recurse(
        dom.documentElement,
        _remove_self_closing,
        dom=dom)

    # Inline and minify SVG img elements
    _recurse(
        dom.documentElement,
        _inline_include,
        source_dir=os.path.dirname(source_path),
        dom=dom,
        files=files)


def _add_manifest(e, manifest_file):
    """Adds an AppCache manifest to e if it is an html element"""
    # Only handle JavaScript elements
    if e.nodeType != Node.ELEMENT_NODE or e.tagName != 'html':
        return

    e.setAttribute('manifest', manifest_file)


def add_manifest(context, manifest_file):
    """Adds an *AppCache* manifest file to all ``html`` elements.

    :param context: The *DOM* context as returned by :func:`start`.

    :param str manifest_file: The path, relative to the document, of the
        *AppCache* manifest file.
    """
    source_path, dom, files = context

    # Add the manifest
    _recurse(
        dom.documentElement,
        _add_manifest,
        manifest_file=manifest_file)
