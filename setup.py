# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import os.path

from codecs import open

from setuptools import setup, find_packages

cwd = os.path.abspath(os.path.dirname(__file__))

with open('README.md', 'r', encoding='utf-8') as f:
    __readme__ = f.read()

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    __changelog__ = f.read()

setup(
    version='2.0.0',
    name='platformshconfig',
    description='Small helper to access Platform.sh environment variables.',
    url='https://github.com/platformsh/platformsh-config-reader-python3',
    author='Platform.sh',
    author_email='sayhello@platform.sh',
    license='MIT',
    long_description=__readme__ + '\n\n' + __changelog__,
    packages=find_packages(),
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
)
