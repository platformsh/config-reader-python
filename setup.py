# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import sys
import os.path

from codecs import open

from setuptools import setup, find_packages
from setuptools.command.install import install

cwd = os.path.abspath(os.path.dirname(__file__))

VERSION = "2.1.1"

with open('README.md', 'r', encoding='utf-8') as f:
    __readme__ = f.read()

with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
    __changelog__ = f.read()

class VerifyVersionCommand(install):
    """Command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

setup(
    version=VERSION,
    name='platformshconfig',
    description='Small helper to access Platform.sh environment variables.',
    url='https://github.com/platformsh/config-reader-python3',
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
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)
