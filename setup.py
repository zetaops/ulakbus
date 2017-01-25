#!/usr/bin/env python
from distutils.core import setup

from setuptools import find_packages

import os
import subprocess


def create_mo_files():
    # http://stackoverflow.com/questions/34070103/how-to-compile-po-gettext-translations-in-setup-py-python-script/37906830#37906830
    data_files = []
    localedir = 'ulakbus/locale'
    po_dirs = [localedir + '/' + l + '/LC_MESSAGES/'
               for l in next(os.walk(localedir))[1]]
    for d in po_dirs:
        mo_files = []
        po_files = [f
                    for f in next(os.walk(d))[2]
                    if os.path.splitext(f)[1] == '.po']
        for po_file in po_files:
            filename, extension = os.path.splitext(po_file)
            mo_file = filename + '.mo'
            msgfmt_cmd = 'msgfmt {} -o {}'.format(d + po_file, d + mo_file)
            subprocess.call(msgfmt_cmd, shell=True)
            mo_files.append(d + mo_file)
        data_files.append((d, mo_files))
    return data_files


setup(
    name='Ulakbus',
    version='0.9.3',
    description='Ulakbus Butunlesik Universite Sistemi',
    author='Zetaops',
    license='GPL v3',
    author_email='info@zetaops.io',
    install_requires=[
        'zengine==0.7.9',
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
    data_files=create_mo_files(),
    keywords=['academic erp', 'universty automation system'],
    classifiers=[]
)
