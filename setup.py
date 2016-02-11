#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(
        name='Ulakbus',
        version='0.0.1',
        description='Ulakbus Butunlesik Universite Sistemi',
        author='Zetaops',
        install_requires=[
            'pyoko==0.7',
            'zengine==0.7',
            'passlib',
            'Werkzeug',
            'requests',
            'boto',
            'reportlab',
            'six'
        ],
        dependency_links=[
            'git+https://github.com/zetaops/pyoko.git@0.7#egg=pyoko',
            'git+https://github.com/zetaops/zengine.git@0.7#egg=zengine'],

        author_email='info@zetaops.io',
        url='https://github.com/zetaops/ulakbus',
        packages=find_packages(exclude=['tests', 'tests.*']),
        package_data={
            'ulakbus': ['diagrams/*.bpmn'],
        }
)
