# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, ListNode
from zengine.forms import fields

from . import RoomType, Okutman, Room, Sube, Donem, Unit, Ders, HAFTA, OgrenciDersi

class DersEtkinligi(Model):

    class Meta:
        verbose_name = "Ders Etkinliği"
        search_fields = ['unit_yoksis_no', 'room', 'okutman']

    solved = fields.Boolean('Ders Planı Çözüm Durumu', index=True)
    unitime_key = fields.String(index=True) #class id
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
    sure = fields.Integer("Ders Etkinliği Süresi",index=True)

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
        """Yeni bir DersEtkinligi oluşturulduğunda arama amaçlı olan alanları otomatik olarak doldurur."""
        self.ders = self.sube.ders
        self.save()

    def __unicode__(self):
        return '%s - %s - %s:%s|%s:%s - %s' % (self.room.name, self.gun, self.baslangic_saat, self.baslangic_dakika,
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
    solved = fields.Boolean('Sınav Planı Çözüm Durumu', index=True, default=False)

    published = fields.Boolean('Sınav Planı Yayınlanma Durumu', index=True, default=False)
    tarih = fields.DateTime('Sınav Tarihi', index=True)


    class SinavYerleri(ListNode):
        room = Room('Sınav Yeri', index=True)

def ogrenci_sinav_etkinligi_getir(ogrenci):

    guncel_donem = Donem.objects.get(guncel=True)
    # Güncel döneme ve giriş yapan, öğrenciye ait öğrenci_dersleri bulunur.
    ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=guncel_donem)

    subeler = []
    # Bulunan öğrenci derslerinin şubeleri bulunur ve listeye eklenir.
    for ogrenci_ders in ogrenci_dersleri:
        try:
            sube = Sube.objects.get(ogrenci_ders.sube.key)
            subeler.append(sube)
        except:
            pass

    sinav_etkinlikleri = []
    for sube in subeler:
        for etkinlik in SinavEtkinligi.objects.filter(published=True, sube=sube, donem=guncel_donem):
            sinav_etkinlikleri.append(etkinlik)

    return sinav_etkinlikleri

def okutman_sinav_etkinligi_getir(okutman):
    guncel_donem = Donem.objects.get(guncel=True)
    subeler = Sube.objects.filter(okutman=okutman, donem=guncel_donem)

    sinav_etkinlikleri = []
    for sube in subeler:
        for etkinlik in SinavEtkinligi.objects.filter(published=True, sube=sube, donem=guncel_donem):
            sinav_etkinlikleri.append(etkinlik)

    return sinav_etkinlikleri