# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field, Model, ListNode
from ulakbus.models import Unit

__author__ = 'Ali Riza Keles'


class Campus(Model):
    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    coordinate_x = field.String("X Koordinatı", index=True)
    coordinate_y = field.String("Y Koordinatı", index=True)

    class Meta:
        verbose_name = "Yerleşke"
        verbose_name_plural = "Yerleşkeler"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.coordinates())

    def coordinates(self):
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class Building(Model):
    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    coordinate_x = field.String("X Koordinatı", index=True)
    coordinate_y = field.String("Y Koordinatı", index=True)
    campus = Campus()

    class Meta:
        verbose_name = "Bina"
        verbose_name_plural = "Binalar"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name', 'campus_display']

    def campus_display(self):
        return "%s" % self.campus.name

    campus_display.title = 'Yerleşke'

    def __unicode__(self):
        return '%s %s %s %s' % (self.code, self.name, self.coordinates(), self.campus)

    def coordinates(self):
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class RoomType(Model):
    type = field.String("Oda Tipi", index=True)
    notes = field.Text("Notlar", index=True)

    def __unicode__(self):
        return '%s' % (self.type)


class Room(Model):
    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    room_type = RoomType("Oda Tipi", index=True)
    floor = field.String("Kat", index=True)
    capacity = field.Integer("Kapasite", index=True)
    building = Building()
    is_active = field.Boolean("Aktif", index=True)

    class Meta:
        verbose_name = "Oda"
        verbose_name_plural = "Odalar"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name', 'building_display']

    def building_display(self):
        return "%s" % self.building.name

    building_display.title = 'Bina'

    class RoomDepartments(ListNode):
        unit = Unit()

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.capacity)
