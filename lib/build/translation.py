import os
import subprocess

from xml.dom import Node
from xml.dom.minidom import parse
from xml.sax import make_parser

from .xmltransform import _recurse

def _add_entry(pofile, entry):
    """Adds a new *PO* entry to a *PO* file.

    If the message is already present in the pofile, it is updated by extending
    the comment and adding a new location.

    :param pofile.POFile pofile: The *PO* file to modify.

    :param pofile.POEntry entry: The entry.
    """
    try:
        pofile.append(entry)
    except ValueError:
        # This is caused by duplicate strings; try to merge them
        other = pofile.find(entry.msgid)
        other.comment += '\n' + entry.comment
        other.occurrences += entry.occurrences


def _extract_x_tr(e, pofile, path):
    """Extracts all text nodes whose parent element has the x-tr attribute"""
    import polib

    if e.nodeType != Node.ELEMENT_NODE or not e.hasAttribute('x-tr'):
        return

    # Make sure that the elements has exactly one child node, and that it is a
    # text node
    if e.childNodes.length != 1 or e.firstChild.nodeType != Node.TEXT_NODE:
        raise RuntimeError('Invalid use of x-tr attribute: %s', e.toxml())

    _add_entry(
        pofile,
        polib.POEntry(
            comment = e.getAttribute('x-tr'),
            msgid = ' '.join(e.firstChild.nodeValue.split()),
            occurrences = [(path, e.parse_position[0])]))


def _extract_javascript(e, pofile, path):
    """Extracts translatable strings from JavaScript files"""
    import polib

    # Only use script tags with src attribute
    if e.nodeType != Node.ELEMENT_NODE \
            or e.tagName != 'script' \
            or not e.hasAttribute('src') \
            or e.getAttribute('x-no-inline') == 'true':
        return

    # Extract and merge messages; use the C# parser to support _('string '
    # + 'concatenation')
    podata = subprocess.check_output(['xgettext',
        os.path.join(
            os.path.dirname(path),
            e.getAttribute('src')),
        '--add-comments',
        '--from-code=utf-8',
        '--language=C#',
        '--keyword=_',
        '--keyword=_N:1,2',
        '--output=-'])
    if podata:
        for entry in polib.pofile(podata):
            _add_entry(pofile, entry)


def read_translatable_strings(path):
    """Reads all translatable strings from an *XHTML* file.

    :param str path: The path to the file.

    :return: a *PO* file instance
    :rtype: polib.POFile
    """
    import polib

    def set_content_handler(dom_handler):
        def start_element_ns(name, tagName , attrs):
            orig_start_cb(name, tagName, attrs)
            cur_elem = dom_handler.elementStack[-1]
            cur_elem.parse_position = (
                parser._parser.CurrentLineNumber,
                parser._parser.CurrentColumnNumber)

        orig_start_cb = dom_handler.startElementNS
        dom_handler.startElementNS = start_element_ns
        orig_set_content_handler(dom_handler)

    # Monkey-patch the parser to store the original location in each node
    parser = make_parser()
    orig_set_content_handler = parser.setContentHandler
    parser.setContentHandler = set_content_handler

    dom = parse(path, parser)

    pofile = polib.POFile(check_for_duplicates = True)
    pofile.metadata['Content-Type'] = 'text/plain; charset=utf-8'
    pofile.metadata['Content-Transfer-Encoding'] = '8bit'

    # Normalise the XML
    _recurse(dom,
        lambda e: e.normalize())

    # Extract all inlined translatable strings
    _recurse(dom, _extract_x_tr,
        pofile = pofile, path = path)

    # Extract messages from JavaScript
    _recurse(dom, _extract_javascript,
        pofile = pofile, path = path)

    return pofile


def merge_catalogs(template, catalog):
    """Merges all new messages from a template with a translation catalogue.

    :param str template: The *POT* file path.

    :param str catalog: The *PO* file path.
    """
    subprocess.call(['msgmerge',
        '--update',
        '--sort-by-file',
        catalog,
        template])
