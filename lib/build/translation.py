from xml.dom.minidom import parse


def read_translatable_strings(path):
    """
    Reads all translatable strings from an XHTML file.

    @param path
        The path to the file.
    @return a polib.POFile instance
    """
    dom = parse(path)

    # TODO: Implement
