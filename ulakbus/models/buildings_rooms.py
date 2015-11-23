# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field, Model

__author__ = 'Ali Riza Keles'


class Campus(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    coordinate_x = field.String("Coordinate X", index=True)
    coordinate_y = field.String("Coordinate Y", index=True)

    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campuses"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.coordinates)

    def coordinates(self):
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class Building(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    coordinate_x = field.String("Coordinate X", index=True)
    coordinate_y = field.String("Coordinate Y", index=True)
    campus = Campus()

    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campuses"
        search_fields = ['name', 'campus']
        list_fields = ['name', 'campus']

    def __unicode__(self):
        return '%s %s %s %s' % (self.code, self.name, self.coordinates, self.campus)

    def coordinates(self):
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class Room(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    floor = field.String("Floor", index=True)
    capacity = field.Integer("Capacity", index=True)
    building = Building()
    campus = Campus()
    is_active = field.Boolean("Active", index=True)

    class Meta:
        verbose_name = "Campus"
        verbose_name_plural = "Campuses"
        search_fields = ['code', 'name', 'campus']
        list_fields = ['code', 'name', 'campus']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.capacity)
