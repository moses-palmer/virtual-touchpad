import os

from xml.dom import Node


def _trim(e):
    """Trims whitespace from start and end of text nodes; CDATA nodes are not
    modified"""
    if e.nodeType == Node.TEXT_NODE:
        e.nodeValue = e.nodeValue.strip()


def _remove_comments(e):
    """Removes comment nodes"""
    if e.nodeType == Node.COMMENT_NODE and e.parentNode:
        e.parentNode.removeChild(e).unlink()


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

    # Normalise the XML
    recurse(dom.documentElement,
        lambda e: e.normalize())

    with open(target_path, 'w') as target:
        target.write('<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html>')
        dom.documentElement.writexml(target)
