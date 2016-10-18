import os
import subprocess

from buildlib import HTML_ROOT, PDIR, ROOT, translation
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


@build_command('generate Python translation catalogues from PO files')
class generate_translations_py(Command):
    SOURCE_DIR = generate_translations_js.SOURCE_DIR
    TARGET_DIR = generate_translations_js.TARGET_DIR

    def run(self):
        for domain, po_path in list_po_from_domain(self.SOURCE_DIR):
            if not domain.endswith('.py'):
                continue

            target = os.path.join(
                self.TARGET_DIR,
                domain.rsplit('.')[0],
                '%s.mo' % os.path.basename(po_path).rsplit('.', 1)[0])

            subprocess.check_call([
                'msgfmt',
                '--output-file', target,
                po_path])


@build_command('update the POT files for XHTML files')
class xgettext_xhtml(Command):
    SOURCES = (
        ('index.js', os.path.join(HTML_ROOT, 'index.xhtml')),
        ('help.js', os.path.join(HTML_ROOT, 'help', 'index.xhtml')))
    TARGET_DIR = os.path.join(
        ROOT,
        'po')

    def run(self):
        for domain, path in self.SOURCES:
            # The POT file is stored immediately in the target directory
            potfile = os.path.join(self.TARGET_DIR, domain + '.pot')

            # Extract the messages and save the POT file
            messages = translation.read_translatable_strings(path)
            messages.save(potfile)

            # Update the old translations
            self.update(self.TARGET_DIR, domain, potfile)

    @staticmethod
    def update(target_dir, domain, potfile):
        """Updates all PO files in a directory with strings from a POT file.

        :param str target_dir: The root directory for translations.

        :param str domain: The domain.

        :param str potfile: The newly generated POT file.
        """
        domain_path = os.path.join(target_dir, domain)
        if not os.path.isdir(domain_path):
            return
        for filename in (
                f
                for f in os.listdir(domain_path)
                if f.endswith('.po')):
            translation.merge_catalogs(
                potfile,
                os.path.join(domain_path, filename))


@build_command('update the POT files for Python files')
class xgettext_py(Command):
    SOURCE_DIR = PDIR
    TARGET_DIR = xgettext_xhtml.TARGET_DIR
    DOMAIN = 'server.py'

    def run(self):
        filenames = []
        for dirpath, dirnames, names in os.walk(self.SOURCE_DIR):
            for name in (f for f in names if f.endswith('.py')):
                filenames.append(
                    os.path.relpath(os.path.join(dirpath, name), ROOT))

        potfile = os.path.join(self.TARGET_DIR, self.DOMAIN + '.pot')
        subprocess.check_output([
            'xgettext',
            '--output=%s' % os.path.relpath(potfile, ROOT),
            '--language=Python',
            '--files-from=-'],
            cwd=ROOT,
            input='\n'.join(filenames),
            universal_newlines=True)

        xgettext_xhtml.update(self.TARGET_DIR, self.DOMAIN, potfile)

@build_command('generate translation catalogues from PO files',
               generate_translations_js,
               generate_translations_py)
class generate_translations(Command):
    pass
