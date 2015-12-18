# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.buildings_rooms import Building, Campus

__author__ = 'Halil İbrahim Yılmaz'


def yeni_bina():
    uni = Unit.objects.filter(parent_unit_no=0)[0]
    campus = Campus.objects.filter()[0]
    faculty_list = Unit.objects.filter(parent_unit_no=uni.yoksis_no)

    for faculty in faculty_list:
        b = Building()
        b.code = faculty.yoksis_no
        b.name = faculty.name
        b.coordinate_x = campus.coordinate_x
        b.coordinate_y = campus.coordinate_y
        b.campus = campus
        b.save()

    print("Fake bina tanımlaması başarılı")
