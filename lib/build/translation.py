from xml.dom.minidom import parse
from xml.sax import make_parser


def read_translatable_strings(path):
    """
    Reads all translatable strings from an XHTML file.

    @param path
        The path to the file.
    @return a polib.POFile instance
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

    # TODO: Extract translatable strings

    return pofile
