# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import os.path

from codecs import open

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with open('README.md', 'r', encoding='utf-8') as f:
    __readme__ = f.read()

with open('CHANGELOG.rst', 'r', encoding='utf-8') as f:
    __changelog__ = f.read()

setup(
    version='0.1.0',
    name='pshconfig',
    description='Small helper to access Platform.sh environment variables.',
    url='https://github.com/platformsh/platformsh-config-reader-python3',
    author='Chad Carlson',
    author_email='chad.carlson@platform.sh',
    license='MIT',
    long_description=__readme__ + '\n\n' + __changelog__,
    packages=find_packages(),
    tests_require=['pytest'],
    classifiers=('Development Status :: 1 - Planning',
                 'License :: OSI Approved :: MIT',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: 3.7',
                 'Programming Language :: Python :: 3 :: Only'),
)
