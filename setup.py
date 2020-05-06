#!/usr/bin/env python3
from os.path import abspath, dirname
from setuptools import setup

import versioneer

AUTHOR = 'mzpqnxow'
CURDIR = abspath(dirname(__file__))
NAMESPACE = ['mzpqnxow']
PACKAGE = 'sillylog'
PROJECT_NAME = 'py{}'.format(PACKAGE)
REQUIRED = []
NAME = '.'.join(NAMESPACE + [PROJECT_NAME])
ABOUT = {}

# Use https://pypi.org/classifiers/ for reference
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Natural Language :: English',
    'Topic :: Software Development :: Libraries']


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name=NAME,
    classifiers=CLASSIFIERS)
