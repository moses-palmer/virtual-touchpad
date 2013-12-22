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

    # Normalise the XML
    recurse(dom.documentElement,
        lambda e: e.normalize())

    with open(target_path, 'w') as target:
        target.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html>')
        dom.documentElement.writexml(target)
