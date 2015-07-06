#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(
    name='Ulakbus',
    version='0.0.1',
    description='Ulakbus Butunlesik Universite Sistemi',
    author='Zetaops',
    requires=['beaker', 'falcon', 'beaker_extensions', 'redis', 'SpiffWorkflow', 'zengine'],
    install_requires=['beaker', 'falcon', 'beaker_extensions', 'redis', 'SpiffWorkflow', 'zengine'],
    dependency_links=['git+https://github.com/didip/beaker_extensions.git#egg=beaker_extensions',
                      'git+https://github.com/zetaops/SpiffWorkflow.git#egg=SpiffWorkflow',
                      'git+https://github.com/zetaops/zengine.git#egg=zengine'],

    author_email='info@zetaops.io',
    url='https://github.com/zetaops/ulakbus',
    packages=find_packages(exclude=['tests', 'tests.*']),
)
