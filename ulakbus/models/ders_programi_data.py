# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, ListNode
from zengine.forms import fields
from . import RoomType, Okutman, Room, Sube, Donem, Unit, Ders


class DersEtkinligi(Model):
    
    class Meta:
        verbose_name = "Ders Etkinligi"
        search_fields = ['unit_yoksis_no', 'room', 'okutman']

    solved = fields.Boolean(index=True)
    unitime_id = fields.String(index=True) #class id
    unit_yoksis_no = fields.Integer(index=True)
    room_type = RoomType(index=True)
    okutman = Okutman("Ogretim Elemani", index=True)
    sube = Sube(index=True)
    donem = Donem("Donem",index = True)
    bolum = Unit(index = True)
    published = fields.Boolean(index=True)
    # Arama amaçlı
    ders = Ders(index=True)

    # to be calculated
    room = Room('Derslik')
    gun = fields.String("Gun")
    baslangic_saat = fields.String("Baslangic Saat")
    baslangic_dakika = fields.String("Baslangic Dakika")
    bitis_saat = fields.String("Bitis Saat")
    bitis_dakika = fields.String("Bitis Dakika")

    def post_creation(self):
        """Yeni bir DersEtkinligi oluşturulduğunda arama amaçlı olan alanları otomatik olarak doldurur."""
        self.ders = self.sube.ders
        self.save()


class SinavEtkinligi(Model):

    class Meta:
        verbose_name = 'Sınav Etkinliği'

    ders = Ders(index=True)
    donem = Donem(index=True)
    bolum = Unit(index=True)
    unitime_id = fields.String(index=True)

    published = fields.Boolean(index=True, default=False)
    tarih = fields.DateTime('Sınav Tarihi', index=True)

    class SinavYerleri(ListNode):
        room = Room('Sınav Yeri', index=True)
