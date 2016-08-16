# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field, ListNode
from ulakbus.lib.date_time_helper import GUN_DILIMI, HAFTA
from ulakbus.models import RoomType, Okutman, Sube, Donem, Unit, Ders, Room
from zengine.forms import fields
from .buildings_rooms import Room
from .auth import Unit
from .ogrenci import Okutman

UYGUNLUK_DURUMU = [
    (1, "Uygun"),
    (2, "Mümkünse Uygun Değil"),
    (3, "Kesinlikle Uygun Değil")
]
DERSLIK_DURUMU = [
    (1, 'Herkese Açık'),
    (2, 'Bölüme Ait'),
    (3, 'Herkese Kapalı')
]


class ZamanDilimleri(Model):
    class Meta:
        unique_together = [('birim', 'gun_dilimi')]
        search_fields = ['birim', 'gun_dilimi']

    birim = Unit('Bölüm')
    gun_dilimi = field.Integer('Gün Dilimi', choices=GUN_DILIMI, index=True)

    baslama_saat = field.String("Başlama Saati", index=True)
    baslama_dakika = field.String("Başlama Dakikası", index=True)

    bitis_saat = field.String("Bitiş Saati", index=True)
    bitis_dakika = field.String("Bitiş Dakikası", index=True)

    # Ara suresi de dahil. Ornek olarak 30 girildiyse ders 9, 9.30, 10 gibi surelerde baslayabilir.
    ders_araligi = field.Integer('Ders Süresi', default=60, index=True)
    ara_suresi = field.Integer('Tenefüs Süresi', default=10, index=True)

    zaman_dilimi_suresi = field.Integer("Zaman Dilimi Süresi", index=True)

    def pre_save(self):
        self.zaman_dilimi_suresi = int(self.bitis_saat) - int(self.baslama_saat)

    def __unicode__(self):
        return '%s - %s:%s|%s:%s' % (dict(GUN_DILIMI)[int(self.gun_dilimi)], self.baslama_saat,
                                     self.baslama_dakika, self.bitis_saat, self.bitis_dakika)


class OgElemaniZamanPlani(Model):
    """
        Okutman, birim ve okutmanin ilgili birimde verecegi  haftalik ders saati bilgisi tutulur.
    """

    class Meta:
        verbose_name = 'Öğretim Elemanı Zaman Kaydı'
        verbose_name_plural = 'Öğretim Elemanı Zaman Kayıtları'
        unique_together = [('okutman', 'birim')]
        search_fields = ['okutman', 'birim']

    okutman = Okutman("Öğretim Elemanı")
    birim = Unit("Birim")
    toplam_ders_saati = field.Integer("Öğretim Elemanı Toplam Ders Saati", index=True)

    def __unicode__(self):
        return '%s - %s' % (self.birim, self.okutman)


class ZamanCetveli(Model):
    """
        Ilgili birime ait belirlenen zaman dilimleri ders program koordinatoru tarafindan
        ogretim elemanlarin saat araliklarina gore durumlarini belirleyecegi model
    """

    class Meta:
        verbose_name = 'Zaman Cetveli'
        unique_together = [('zaman_dilimi', 'ogretim_elemani_zaman_plani', 'gun')]
        search_fields = ['zaman_dilimi', 'ogretim_elemani_zaman_plani', 'birim', 'gun', 'durum']

    birim = Unit("Birim")
    gun = field.Integer("Gün", choices=HAFTA, index=True)
    zaman_dilimi = ZamanDilimleri("Zaman Dilimi")
    durum = field.Integer("Uygunluk Durumu", choices=UYGUNLUK_DURUMU, default=1, index=True)
    ogretim_elemani_zaman_plani = OgElemaniZamanPlani("Öğretim Elemanı")

    def __unicode__(self):
        return '%s - %s - %s' % (self.ogretim_elemani_zaman_plani, self.zaman_dilimi,
                                 dict(UYGUNLUK_DURUMU)[int(self.durum)])


class DerslikZamanPlani(Model):
    class Meta:
        verbose_name = 'Derslik Zaman Planı'
        unique_together = [
            ('derslik', 'gun', 'baslangic_saat', 'baslangic_dakika', 'bitis_saat', 'bitis_dakika')]
        search_fields = ['unit', 'derslik', 'gun', 'derslik_durum']

    unit = Unit()
    derslik = Room()
    gun = field.Integer("Gün", choices=HAFTA, index=True)
    baslangic_saat = field.String('Başlangıç Saati', default='08', index=True)
    baslangic_dakika = field.String('Başlangıç Dakikası', default='30', index=True)
    bitis_saat = field.String("Bitiş Saati", default='12', index=True)
    bitis_dakika = field.String("Bitiş Dakikası", default='00', index=True)
    derslik_durum = field.Integer("Durum", choices=DERSLIK_DURUMU, index=True)

    def __unicode__(self):
        return '%s %s %s:%s|%s:%s %s' % (self.derslik, dict(HAFTA)[self.gun],
                                         self.baslangic_saat, self.baslangic_dakika,
                                         self.bitis_saat, self.bitis_dakika,
                                         dict(DERSLIK_DURUMU)[int(self.derslik_durum)])


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
        return '{} {} {}'.format(self.ders.ad, self.sube.ad, self.sinav_zamani())

    def sinav_zamani(self):
        return '{:%Y.%m.%d - %H:%M}'.format(self.tarih) if self.tarih else 'Henüz zamanlanmadi'