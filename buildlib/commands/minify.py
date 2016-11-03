import os

import buildlib

from . import build_command, Command


@build_command('minify html files')
class minify_html(Command):
    FILES = (
        ('index.xhtml', True),
        ('help/index.xhtml', False))

    def minify(self, name, include_appcache):
        dom_context = buildlib.xmltransform.start(
            os.path.join(
                buildlib.HTML_ROOT,
                name))

        buildlib.xmltransform.minify_html(dom_context)

        if include_appcache:
            buildlib.xmltransform.add_manifest(
                dom_context,
                'virtual-touchpad.appcache')

        buildlib.xmltransform.end(
            dom_context,
            os.path.join(
                buildlib.HTML_ROOT,
                name + '.min'))

    def run(self):
        for name, include_appcache in self.FILES:
            self.minify(name, include_appcache)
