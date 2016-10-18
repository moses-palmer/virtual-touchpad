import os

from buildlib import PDIR, ROOT
from . import build_command, Command


def list_po_from_domain(path):
    """Lists all PO files found under a root directory.

    This function will yield tuples on the form
    ``(domain, os.path.join(path, domain, name_po))``.

    :param str path: The source directory.
    """
    for domain, domain_path in (
            (
                domain,
                os.path.join(path, domain))
            for domain in os.listdir(path)
            if os.path.isdir(os.path.join(path, domain))):
        yield from (
                (
                    domain,
                    os.path.join(domain_path, name))
                for name in os.listdir(domain_path)
                if name.endswith('.po'))


@build_command('generate Javascript translation catalogues from PO files')
class generate_translations_js(Command):
    SOURCE_DIR = os.path.join(
        ROOT,
        'po')
    TARGET_DIR = os.path.join(
        PDIR,
        'translations')

    def run(self):
        import json

        for domain, po_path in list_po_from_domain(self.SOURCE_DIR):
            if not domain.endswith('.js'):
                continue

            code, catalog = self.generate_catalog(po_path)
            with open(os.path.join(
                    self.TARGET_DIR,
                    domain.rsplit('.')[0],
                    code + '.js'), 'w') as f:
                f.write('exports.translation.catalog=')
                json.dump(catalog, f)

    def generate_catalog(self, language_path):
        import polib

        # Load the PO file
        pofile = polib.pofile(language_path)

        # Extract interesting meta data
        code = pofile.metadata['Language']
        plurals = {
            key.strip(): value.strip()
            for (key, value) in (
                keyvalue.split('=', 1)
                for keyvalue in pofile.metadata[
                    'Plural-Forms'].split(';')
                if keyvalue)}

        # Create the catalogue skeleton
        texts = {}
        catalog = {}
        catalog['code'] = code
        catalog['plural'] = plurals['plural']
        catalog['texts'] = texts

        # Populate the catalogue from the PO file
        for entry in pofile:
            texts[entry.msgid] = self.create_entry(entry, plurals)

        return code, catalog

    def create_entry(self, entry, plurals):
        # If this is a plural string, we first create a list of empty strings
        # and then populate it, otherwise we simply return the string
        if entry.msgid_plural:
            result = [''] * int(plurals['nplurals'])
            for n, msgstr in entry.msgstr_plural.items():
                result[int(n)] = msgstr
            return result

        else:
            return entry.msgstr


@build_command('generate translation catalogues from PO files',
               generate_translations_js)
class generate_translations(Command):
    pass
