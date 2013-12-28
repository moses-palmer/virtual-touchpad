import os

from xml.dom import Node
from xml.dom.minidom import CDATASection


def _trim(e):
    """Trims whitespace from start and end of text nodes; CDATA nodes are not
    modified"""
    if e.nodeType == Node.TEXT_NODE:
        e.nodeValue = e.nodeValue.strip()


def _remove_comments(e):
    """Removes comment nodes"""
    if e.nodeType == Node.COMMENT_NODE and e.parentNode:
        e.parentNode.removeChild(e).unlink()


def _inline_script(e, source_dir, dom):
    """Inlines script tags"""
    # Only use script tags with src attribute
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'script' \
            or not e.hasAttribute('src'):
        return

    # Read the script source and inline it
    src_path = os.path.join(
        source_dir,
        e.getAttribute('src'))
    with open(src_path) as src:
        cdata = CDATASection()
        cdata.replaceWholeText(src.read())
        e.appendChild(cdata)

    # Make sure to remove the src attribute
    e.removeAttribute('src')


def _inline_css(e, source_dir, dom):
    """Inlines CSS"""
    # Only use CSS stylesheet tags
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'link' \
            or e.getAttribute('rel') != 'stylesheet' \
            or e.getAttribute('type') != 'text/css':
        return

    # Read the stylesheet and inline it
    href_path = os.path.join(
        source_dir,
        e.getAttribute('href'))
    with open(href_path) as href:
        cdata = CDATASection()
        cdata.replaceWholeText(href.read())
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


def _join_elements(e):
    """Joins consecutive similar script and style elements"""
    # Only handle script and style tags
    if e.nodeType != Node.ELEMENT_NODE \
            or not e.tagName in ('script', 'style'):
        return

    # Move next sibling's child nodes to this node while next sibling is
    # same type
    while e.nextSibling and e.nextSibling.nodeType == Node.ELEMENT_NODE \
            and e.tagName == e.nextSibling.tagName:
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
        c.replaceWholeText(slimit.minify(c.wholeText,
            mangle = True,
            mangle_toplevel = True))


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


_VOID_ELEMENTS = tuple(e.strip() for e in
    'area, base, br, col, embed, hr, img, input, keygen, link, meta, param, '
    'source, track, wbr'.split(','))
def _remove_self_closing(e, dom):
    """Makes sure that only void elements are self closing"""
    # Only handle non-void elements
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName in _VOID_ELEMENTS:
        return

    if len(e.childNodes) == 0:
        e.appendChild(dom.createTextNode(''))


def html(source_path, target_path):
    """
    Minifies an HTML file.

    @param source_path
        The HTML file which to modify
    @param target_path
        The output file.
    """
    from xml.dom.minidom import parse

    dom = parse(source_path)

    def recurse(e, callback, **kwargs):
        callback(e, **kwargs)
        for s in e.childNodes:
            recurse(s, callback, **kwargs)

    # Trim text nodes
    recurse(dom.documentElement, _trim)

    # Remove comments
    recurse(dom.documentElement, _remove_comments)

    # Inline script tags
    recurse(dom.documentElement, _inline_script,
        source_dir = os.path.dirname(source_path),
        dom = dom)

    # Inline CSS tags
    recurse(dom.documentElement, _inline_css,
        source_dir = os.path.dirname(source_path),
        dom = dom)

    # Normalise the XML
    recurse(dom.documentElement,
        lambda e: e.normalize())

    # Join similar elements
    recurse(dom.documentElement, _join_elements)

    # Minify JavaScript
    recurse(dom.documentElement, _minify_js)

    # Minify CSS
    recurse(dom.documentElement, _minify_css)

    # Make sure only void elements are self-closing
    recurse(dom.documentElement, _remove_self_closing,
        dom = dom)

    with open(target_path, 'w') as target:
        target.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html>')
        dom.documentElement.writexml(target)

