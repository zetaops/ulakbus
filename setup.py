#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

setup(
    name='Ulakbus',
    version='0.9.0',
    description='Ulakbus Butunlesik Universite Sistemi',
    author='Zetaops',
    license='GPL v3',
    author_email='info@zetaops.io',
    install_requires=[
        'zengine==0.7.7',
        'requests',
        'boto',
        'reportlab',
        'six',
        'lxml',
        'streamingxmlwriter',
        'dateutils'
    ],
    url='https://github.com/zetaops/ulakbus',
    packages=find_packages(exclude=['tests', 'tests.*']),
    download_url='https://github.com/zetaops/ulakbus/archive/master.zip',
    package_data={
        'ulakbus': ['diagrams/*.bpmn'],
    },
    keywords=['academic erp', 'universty automation system'],
    classifiers=[]
)
