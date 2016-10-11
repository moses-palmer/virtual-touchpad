# -*- mode: python -*-

import fnmatch
import os
import sys

import virtualtouchpad._info as INFO


VERSION = '.'.join(str(v) for v in INFO.__version__)
PLATFORM = ''.join(c for c in sys.platform if c.isalpha())
NAME = 'VirtualTouchpad'
SCRIPTS = [
    os.path.join('../scripts/virtual-touchpad.py')]
ICON = 'build/icons/icon-%s.%s' % (
    PLATFORM,
    {
        'darwin': 'icns',
        'linux': 'png',
        'win': 'ico'}[PLATFORM])

IGNORE = (
    '/usr/share/*',)


a = Analysis(
    SCRIPTS,
    pathex=['pyi'],
    binaries=None,
    datas=[
        ('../lib/virtualtouchpad/html', 'virtualtouchpad/html')],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None)
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    [
        (target, source, tag)
        for (target, source, tag) in a.datas
        if not any(
            fnmatch.fnmatch(source, ignore)
            for ignore in IGNORE)],
    icon=ICON,
    name=NAME,
    debug=False,
    strip=False,
    upx=True,
    console=False)
app = BUNDLE(
    exe,
    name='%s.app' % NAME,
    icon=ICON,
    bundle_identifier='com.newrainsoftware.virtualtouchpad',
    info_plist=dict(
        CFBundleVersion=VERSION,
        CFBundleShortVersionString=VERSION))
