# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import Program, Donem
import datetime

__author__ = 'Halil İbrahim Yılmaz'


def yeni_program():
    program_list = Unit.objects.filter(unit_type='Program')
    term = Donem.objects.filter(guncel=True)[0]
    program_year = term.baslangic_tarihi.year

    for program in program_list:
        bolum = Unit.objects.filter(yoksis_no=program.parent_unit_no)[0]
        p = Program()
        p.yoksis_no = program.yoksis_no
        p.bolum = bolum.name
        p.yil = program_year
        p.adi = program.name
        p.birim = bolum
        p.save()
