#!/usr/bin/env python
# coding: utf8

import os
import sys

from setuptools import setup, find_packages


setup(
    name = 'virtual-touchpad',
    description = ''
        'Turns your mobile or tablet into a touchpad and keyboard for your '
        'computer.',

    install_requires = [
        'bottle >=0.11',
        'gevent >=0.13',
        'gevent-websocket >=0.9'],

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
