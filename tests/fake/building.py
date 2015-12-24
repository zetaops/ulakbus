# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.buildings_rooms import Building, Campus, Room, RoomType
from general import fake, ints
import random

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
        yeni_derslik(building=b,parent_unit_no=faculty.yoksis_no,count=random.choice(range(1, 10)))


    print("Fake bina ve oda tanımlaması başarılı")


def yeni_derslik(building,parent_unit_no,count=1):
    unit_list = Unit.objects.filter(parent_unit_no=parent_unit_no,unit_type="Bölüm")
    for i in range(1, count):
        room = Room(
                code=fake.classroom_code(),
                name=fake.classroom(),
                building=building,
                room_type=random.choice(RoomType.objects.filter()),
                floor=ints(2),
                capacity=random.choice(range(30, 100)),
                is_active=True
        )
        for unit in unit_list:
            room.RoomDepartments(unit=unit)
        room.save()