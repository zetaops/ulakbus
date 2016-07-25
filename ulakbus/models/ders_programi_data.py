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
        verbose_name = "Ders Etkinliği"
        search_fields = ['unit_yoksis_no', 'room', 'okutman']

    solved = fields.Boolean('Ders Planı Çözüm Durumu', index=True)
    unitime_id = fields.String(index=True) #class id
    unit_yoksis_no = fields.Integer('Bölüm Yöksis Numarası', index=True)
    room_type = RoomType('İşleneceği Oda Türü', index=True)
    okutman = Okutman("Öğretim Elemanı", index=True)
    sube = Sube('Şube', index=True)
    donem = Donem('Dönem',index = True)
    bolum = Unit('Bölüm', index = True)
    published = fields.Boolean('Ders Planı Yayınlanma Durumu', index=True)
    # Arama amaçlı
    ders = Ders('Ders', index=True)

    # to be calculated
    room = Room('Derslik')
    gun = fields.String("Gün")
    baslangic_saat = fields.String("Başlangıç Saati")
    baslangic_dakika = fields.String("Başlangıç Dakikası")
    bitis_saat = fields.String("Bitiş Saati")
    bitis_dakika = fields.String("Bitiş Dakikası")

    def post_creation(self):
        """Yeni bir DersEtkinligi oluşturulduğunda arama amaçlı olan alanları otomatik olarak doldurur."""
        self.ders = self.sube.ders
        self.save()


class SinavEtkinligi(Model):

    class Meta:
        verbose_name = 'Sınav Etkinliği'

    sube = Sube('Şube', index=True)
    ders = Ders('Ders', index=True)
    donem = Donem('Dönem', index=True)
    bolum = Unit('Bölüm', index=True)
    unitime_id = fields.String(index=True)
    solved = fields.Boolean('Sınav Planı Çözüm Durumu', index=True, default=False)

    published = fields.Boolean('Sınav Planı Yayınlanma Durumu', index=True, default=False)
    tarih = fields.DateTime('Sınav Tarihi', index=True)

    class SinavYerleri(ListNode):
        room = Room('Sınav Yeri', index=True)
