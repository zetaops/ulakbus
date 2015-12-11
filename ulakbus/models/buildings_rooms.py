# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import field, Model, ListNode

__author__ = 'Ali Riza Keles'

VALUE = 1
OPTIONS = 2
ROOM_FEATURE_TYPES = [
    (VALUE, 'Value'),
    (OPTIONS, 'Options'),
]


def get_choices_val_string(choices, val):
    return dict(choices).get(val)


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


class Room(Model):
    code = field.String("Code", index=True)
    name = field.String("Name", index=True)
    room_type = RoomType("Room Type", index=True)
    floor = field.String("Floor", index=True)
    capacity = field.Integer("Capacity", index=True)
    building = Building()
    is_active = field.Boolean("Active", index=True)

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


class RoomFeature(Model):
    feature_name = field.String()
    type = field.Integer(choices=ROOM_FEATURE_TYPES)

    def __unicode__(self):
        return '%s - %s' % (self.feature_name, self.type)


class RoomOption(Model):
    """
    Burada bekledigimiz ozellikllerin acik bir sekilde seceneklerinin tutulmasidir.
    Koltuk rengi 3 secenege sahiptir.
    Projeksiyon var mi? sorusunun yaniti 0 veya 1 dir.
    Perde sayisi 1 veya 2 dir.

    +-------------------------------------------------------+
    | Feature(Link)            | Option String | Option Int |
    |=======================================================|
    | Koltuk Rengi(1)          | Kirmizi       |            |
    +--------------------------+---------------+------------+
    | Koltuk Rengi(1)          | Mavi          |            |
    +--------------------------+---------------+------------+
    | Koltuk Rengi(1)          | Beyaz         |            |
    +--------------------------+---------------+------------+
    | Projeksyion var mi?(2)   |               | 1          |
    +--------------------------+---------------+------------+
    | Projeksyion var mi?(2)   |               | 0          |
    +--------------------------+---------------+------------+
    | Perde Sayisi(3)          |               | 1          |
    +--------------------------+---------------+------------+
    | Perde Sayisi(3)          |               | 2          |
    +--------------------------+---------------+------------+

    Buna uygun olarak 3 field tanimladik. Kolay filtreleme (x > m, x < n, m < x < n) ozelligi icin
    option int ve string ayri tutuyoruz.

    Burada dikkat edilmesi gereken nokta, ayni feature farkli field typelarda degerlere sahip olmamalidir.
    """

    feature = RoomFeature()
    option_string = field.String()
    option_int = field.Integer()

    def __unicode__(self):
        return '%s - %s' % (self.feature.feature_name, self.option)

    @property
    def option(self):
        return self.option_int or self.option_string


class RoomFeatureOptionVals(Model):
    """
    Arama kolayligi icin tum degerleri buraya kopyaliyoruz.
    """
    val_string = field.String()
    val_int = field.String()
    feature = RoomFeature()
    room = Room()
    option = RoomOption()  # bu baglantiya sadece sonraki guncellemelerde ihtiyacimiz var.

    def __unicode__(self):
        return '%s - %s' % (self.feature.feature_name, self.option_value)

    @property
    def option_value(self):
        return self.val_int or self.val_string
