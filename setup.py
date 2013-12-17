#!/usr/bin/env python
# coding: utf8

import os
import sys

# Make sure we can import build
sys.path.append(os.path.join(
    os.path.dirname(__file__),
    'lib'))
import build

from setuptools import setup, find_packages


setup(
    name = 'virtual-touchpad',
    version = '.'.join(str(i) for i in build.info['version']),
    description = ''
        'Turns your mobile or tablet into a touchpad and keyboard for your '
        'computer.',
    long_description = build.README,

    install_requires = [
        'bottle >=0.11',
        'gevent >=0.13',
        'gevent-websocket >=0.9'] + build.platform_requirements(),

    author = build.info['author'],
    author_email = 'moses.palmer@gmail.com',

    url = 'https://github.com/moses-palmer/virtual-touchpad',

    packages = find_packages(os.path.join(os.path.dirname(__file__), 'lib')),
    package_dir = {
        'virtualtouchpad': 'lib/virtualtouchpad'},
    package_data = {
        'virtualtouchpad': ['_res/*']},

    license = 'GPLv3',
    platforms = ['linux'],
    classifiers = [])
