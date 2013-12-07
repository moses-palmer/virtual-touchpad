#!/usr/bin/env python
# coding: utf8

import os
import sys

from setuptools import setup, find_packages


# Read globals from virtualtouchpad._info without loading it
info = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        'virtualtouchpad',
        '_info.py')) as f:
    for line in f:
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                info[name[2:-2]] = eval(value)
        except ValueError:
            pass


setup(
    name = 'virtual-touchpad',
    version = '.'.join(str(i) for i in info['version']),
    description = ''
        'Turns your mobile or tablet into a touchpad and keyboard for your '
        'computer.',

    install_requires = [
        'bottle >=0.11',
        'gevent >=0.13',
        'gevent-websocket >=0.9'],

    author = info['author'],
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
