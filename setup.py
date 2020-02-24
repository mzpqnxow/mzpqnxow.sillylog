#!/usr/bin/env python3
from __future__ import print_function
import versioneer
from os.path import (
    abspath,
    dirname)
from setuptools import (
    setup,
    find_packages)

AUTHOR = 'mzpqnxow'
CURDIR = abspath(dirname(__file__))
NAMESPACE = ['mzpqnxow']
PACKAGE = 'sillylog'
PROJECT_NAME = '{}'.format(PACKAGE)
DESCRIPTION = 'A package containing common reusable functions and classes'
URL = 'https://github.com/{}/{}'.format(AUTHOR, PROJECT_NAME)
EMAIL = 'copyright@mzpqnxow.com'
LICENSE = 'BSD 3-Clause'
REQUIRED = ['jinja2', 'ujson']

NAME = '.'.join(NAMESPACE + [PROJECT_NAME])
NAME = PROJECT_NAME
ABOUT = {}

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    name=NAME,
    packages=find_packages(),
    install_requires=REQUIRED,
    author=AUTHOR,
    author_email=EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL)
