#!/usr/bin/env python3

# distutils have no entry_points, fail if setuptools are not available
from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Full list of classifiers can be found here:
# https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLS = (
  'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
  'Development Status :: 3 - Alpha',
  'Environment :: Web Environment',
  'Intended Audience :: System Administrators',
  'Operating System :: Unix',
  'Programming Language :: Python',
  'Topic :: Internet :: Log Analysis'
)
REQS = (
    'requests >= 2.18',
    'beautifulsoup4 >= 4.6'
)
CONSOLE_SCRIPTS = (
    'ehdb-fix-tags=eh_docbot.command_line:fix_tags',
    'ehdb-tricky-tags=eh_docbot.command_line:tricky_tags'
)
SRC = 'src'
TESTS = ('*.tests', 'tests.*', '*.tests.*', 'tests')

setup(
    name             = 'eh_docbot',
    description      = 'bot maintainer of the eh documentation consistency',
    version          = '0.1',
    author           = 'Neptune Penguin',
    author_email     = 'admin@neptunepenguin.net',
    license          = 'GNU General Public License, version 3 or later',
    url              = 'https://github.com/neptunepenguin/eh_docbot',
    long_description = read('README'),
    packages         = find_packages(SRC, exclude=TESTS),
    package_dir      = {'': SRC},
    classifiers      = CLS,
    install_requires = REQS,
    entry_points     = {
        'console_scripts' : CONSOLE_SCRIPTS
    }
)

