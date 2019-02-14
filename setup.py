# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""

import os.path
import sys

from codecs import open

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(cwd, 'app', '__version__.py'), 'r', encoding='utf-8') as f:
    exec(f.read())

with open('README.rst', 'r', encoding='utf-8') as f:
    __readme__ = f.read()

with open('CHANGELOG.rst', 'r', encoding='utf-8') as f:
    __changelog__ = f.read()


setup(

    name         = __title__,
    description  = __description__,
    url          = __url__,

    author       = __author__,
    author_email = __author_email__,

    license      = __license__,

    long_description = __readme__ + '\n\n' + __changelog__,

    packages     = find_packages(),

    tests_require=['pytest'],

    classifiers=(
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ),
)