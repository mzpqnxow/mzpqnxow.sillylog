#!/usr/bin/env python3
"""Standard setuptools setup.py script using versioneer"""

# Python Standard Libraries
from os.path import abspath, dirname

# External Dependencies
from setuptools import find_packages, setup

# Package Imports
import versioneer

AUTHOR = 'mzpqnxow'
CURDIR = abspath(dirname(__file__))
NAMESPACE = ['mzpqnxow']
PACKAGE = 'sillylog'
PROJECT_NAME = '{}.{}'.format('.'.join(NAMESPACE), PACKAGE)
DESCRIPTION = 'A package containing common reusable functions and classes'
URL = 'https://github.com/{}/{}'.format(AUTHOR, PROJECT_NAME)
EMAIL = 'copyright@mzpqnxow.com'
LICENSE = 'BSD 3-Clause'
REQUIRED = [
    'jinja2', 'ujson']

NAME = '.'.join(NAMESPACE + [PROJECT_NAME])
NAME = PROJECT_NAME
ABOUT = {}

# Use https://pypi.org/classifiers/ for reference
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
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
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    install_requires=REQUIRED,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL)
