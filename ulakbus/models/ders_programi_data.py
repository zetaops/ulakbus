# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, ListNode
from zengine.forms import fields
from .buildings_rooms import RoomType, Room
from .ogrenci import Okutman, Sube, Donem, Ders
from .ders_programi import HAFTA
from .auth import Unit


class DersEtkinligi(Model):
    class Meta:
        verbose_name = "Ders Etkinliği"
        search_fields = ['unit_yoksis_no', 'room', 'okutman']

    solved = fields.Boolean('Ders Planı Çözüm Durumu', index=True)
    unitime_key = fields.String(index=True)  # class id
    unit_yoksis_no = fields.Integer('Bölüm Yöksis Numarası', index=True)
    room_type = RoomType('İşleneceği Oda Türü', index=True)
    okutman = Okutman("Öğretim Elemanı", index=True)
    sube = Sube('Şube', index=True)
    donem = Donem('Dönem', index=True)
    bolum = Unit('Bölüm', index=True)
    published = fields.Boolean('Ders Planı Yayınlanma Durumu', index=True)
    # Arama amaçlı
    ders = Ders('Ders', index=True)
    ek_ders = fields.Boolean(index=True)
    sure = fields.Integer("Ders Etkinliği Süresi", index=True)

    # teori = field.Integer("Ders Teori Saati", index=True)
    # uygulama = field.Integer("Ders Uygulama Saati", index=True)
    # dersin süresinin ne kadarı teori ne kadarı uygulama gibi 2+2, 4+0 gibi

    # to be calculated
    room = Room('Derslik')
    gun = fields.String("Gün", choices=HAFTA)
    baslangic_saat = fields.String("Başlangıç Saati")
    baslangic_dakika = fields.String("Başlangıç Dakikası")
    bitis_saat = fields.String("Bitiş Saati")
    bitis_dakika = fields.String("Bitiş Dakikası")

    def post_creation(self):
        """Yeni bir DersEtkinligi oluşturulduğunda arama amaçlı olan
        alanları otomatik olarak doldurur."""
        self.ders = self.sube.ders
        self.save()

    def __unicode__(self):
        return '%s - %s - %s:%s|%s:%s - %s' % (
            self.room.name, self.gun, self.baslangic_saat, self.baslangic_dakika,
            self.bitis_saat, self.bitis_dakika, self.okutman)


class SinavEtkinligi(Model):
    class Meta:
        verbose_name = 'Sınav Etkinliği'
        search_field = ['bolum', 'ders', 'sube', 'donem']

    sube = Sube('Şube', index=True)
    ders = Ders('Ders', index=True)
    donem = Donem('Dönem', index=True)
    bolum = Unit('Bölüm', index=True)
    unitime_key = fields.String(index=True)
    # default False, unitime solver tarafindan True yapilir.
    solved = fields.Boolean('Sınav Planı Çözüm Durumu', index=True, default=False)

    # unitime cozumunun ardindan, is akisiyla sinav takvimi yayinlanip True yapilir.
    published = fields.Boolean('Sınav Planı Yayınlanma Durumu', index=True, default=False)

    # sistem servisiyle sinavlarin ardindan True yapilir.
    archived = fields.Boolean('Arşivlenmiş', default=False, index=True)

    tarih = fields.DateTime('Sınav Tarihi', index=True)

    class SinavYerleri(ListNode):
        room = Room('Sınav Yeri', index=True)

    @classmethod
    def sube_sinav_listesi(cls, sube, archived=False, donem=None):
        """
        Şubeye, döneme ve arşive göre sınav etkinliği listesi döndürür.

        """
        donem = donem or Donem.guncel_donem()
        return [e for e in cls.objects.filter(published=True, sube=sube,  archived=archived,
                                              donem=donem).order_by('-tarih')]

    def __unicode__(self):
        return '{} {} {}'.format(self.ders.ad, self.sube.ad, self.sinav_zamani)

    def sinav_zamani(self):
        return '{:%Y.%m.%d - %H:%M}'.format(self.tarih) if self.tarih else 'Henüz zamanlanmadi'
