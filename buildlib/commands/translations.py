import os

from buildlib import PDIR, ROOT
from . import build_command, Command


@build_command('generate translation catalogues from PO files')
class generate_translations(Command):
    def run(self):
        import json

        source_dir = os.path.join(
            ROOT,
            'po')
        target_dir = os.path.join(
            PDIR,
            'translations')

        for domain in os.listdir(source_dir):
            domain_path = os.path.join(source_dir, domain)
            if not os.path.isdir(domain_path):
                continue

            for language in os.listdir(domain_path):
                language_path = os.path.join(domain_path, language)
                if not language_path.endswith('.po'):
                    continue

                code, catalog = self.generate_catalog(language_path)
                with open(os.path.join(
                        target_dir,
                        domain,
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
