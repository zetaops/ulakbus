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
        verbose_name = "Yerleşke"
        verbose_name_plural = "Yerleşkeler"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.coordinates())

    def coordinates(self):
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class Building(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    coordinate_x = field.String("Coordinate X", index=True)
    coordinate_y = field.String("Coordinate Y", index=True)
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
    type = field.String("Room Type", index=True)
    notes = field.Text("Notes", index=True)

    def __unicode__(self):
        return '%s' % self.type


class RoomFeature(Model):
    feature_name = field.String()
    type = field.Integer(choices='room_feature_types')

    def __unicode__(self):
        return '%s - %s' % (self.feature, self.type)


class RoomFeatureValue(Model):
    feature = RoomFeature()
    val = field.String()
    option = RoomFeatureOption()

    @property
    def value(self):
        return self.val if self.val else self.option.option_value

    def __unicode__(self):
        return '%s  - %s' % (self.feature.feature_name, self.value)


class RoomFeatureOption(Model):
    feature = RoomFeature()
    option_value = field.String()

    def __unicode__(self):
        return '%s - %s' % (self.feature.feature_name, self.option_value)


class Room(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    room_type = RoomType("Room Type", index=True)
    floor = field.String("Floor", index=True)
    capacity = field.Integer("Capacity", index=True)
    building = Building()
    is_active = field.Boolean("Active", index=True)

    class Features(ListNode):
        feature = RoomFeatureValue()

    class Meta:
        verbose_name = "Oda"
        verbose_name_plural = "Odalar"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name', 'building_display']

    def building_display(self):
        return "%s" % self.building.name

    building_display.title = 'Bina'

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.capacity)
