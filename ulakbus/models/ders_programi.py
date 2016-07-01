# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Öğrenci Modülü

Bu modül Ulakbüs uygulaması için öğrenci modeli ve öğrenciyle ilişkili data modellerini içerir.

"""

from pyoko import Model, field
from .buildings_rooms import Room
from .auth import Unit
from .ogrenci import Okutman

UYGUNLUK_DURUMU = [
    (1, "Uygun"),
    (2, "Mumkunse Uygun Degil"),
    (3, "Kesinlikle Uygun Degil")
]

HAFTA_ICI_GUNLER = [
    (1, "Pazartesi"),
    (2, "Sali"),
    (3, "Carsamba"),
    (4, "Persembe"),
    (5, "Cuma")
]

HAFTA_SONU_GUNLER = [
    (6, "Ctesi"),
    (7, "Pazar")
]

DERSLIK_DURUMU = [
    (1, 'Herkese Acik'),
    (2, 'Bolume Ait'),
    (3, 'Herkese Kapali')
]

GUN_DILIMI = [
    (1, 'Sabah'),
    (2, 'Ogle'),
    (3, 'Aksam')
]

HAFTA = HAFTA_ICI_GUNLER + HAFTA_SONU_GUNLER


class ZamanDilimleri(Model):

    class Meta:
        unique_together = [('birim', 'gun_dilimi')]
        search_fields = ['birim', 'gun_dilimi']

    birim = Unit('Bolum')
    gun_dilimi = field.Integer('Gun Dilimi', choices=GUN_DILIMI, index=True)

    baslama_saat = field.String("Baslama Saat", default='08', index=True)
    baslama_dakika = field.String("Baslama Dakika", default='00', index=True)

    bitis_saat = field.String("Bitis Saat", default='12', index=True)
    bitis_dakika = field.String("Bitis Dakika", default='00', index=True)

    # Ara suresi de dahil. Ornek olarak 30 girildiyse ders 9, 9.30, 10 gibi surelerde baslayabilir.
    ders_araligi = field.Integer('Ders Suresi', default=60, index=True)
    ara_suresi = field.Integer('Tenefus', default=10, index=True)

    def __unicode__(self):
        return '%s - %s:%s|%s:%s' % (dict(HAFTA_ICI_GUNLER)[int(self.gun_dilimi)], self.baslama_saat,
                                     self.baslama_dakika, self.bitis_saat, self.bitis_dakika)


class OgElemaniZamanPlani(Model):
    """
        Okutman, birim ve okutmanin ilgili birimde verecegi  haftalik ders saati bilgisi tutulur.
    """

    class Meta:
        verbose_name = 'Ogretim Elemani Zaman Kaydi'
        verbose_name_plural = 'Ogretim Elemanlari Zaman Kaydi'
        unique_together = [('okutman', 'birim')]
        search_fields = ['okutman', 'birim']

    okutman = Okutman("Okutman")
    birim = Unit("Birim")
    toplam_ders_saati = field.Integer("Ogretim Elemani Toplam Ders Saati", index=True)

    def __unicode__(self):
        return '%s - %s' % (self.birim, self.okutman)


class ZamanCetveli(Model):
    """
        Ilgili birime ait belirlenen zaman dilimleri ders program koordinatoru tarafindan
        ogretim elemanlarin saat araliklarina gore durumlarini belirleyecegi model
    """
    class Meta:
        verbose_name = 'Zaman Cetveli'
        unique_together = [('zaman_dilimi', 'ogretim_elemani_zaman_plani')]
        search_fields = ['zaman_dilimi', 'ogretim_elemani_zaman_plani', 'birim']

    birim = Unit("Birim")
    gun = field.Integer("Gun", choices=HAFTA, index=True)
    zaman_dilimi = ZamanDilimleri("Zaman Dilimi")
    durum = field.Integer("Uygunluk Durumu", choices=UYGUNLUK_DURUMU, default=1, index=True)
    ogretim_elemani_zaman_plani = OgElemaniZamanPlani("Ogretim Elemani")

    def __unicode__(self):
        return '%s - %s - %s' % (self.ogretim_elemani_zaman_plani, self.zaman_dilimi,
                                 dict(UYGUNLUK_DURUMU)[int(self.durum)])


class DerslikZamanPlani(Model):

    class Meta:
        verbose_name = 'Derslik Zaman Plani'
        unique_together = [('derslik', 'gun', 'baslangic_saat', 'baslangic_dakika', 'bitis_saat', 'bitis_dakika')]
        search_fields = ['unit', 'derslik', 'gun', 'derslik_durum']

    unit = Unit()
    derslik = Room()
    gun = field.Integer("Gun", choices=HAFTA, index=True)
    baslangic_saat = field.String('Baslangic Saat', default='08', index=True)
    baslangic_dakika = field.String('Baslangic Dakika', default='30', index=True)
    bitis_saat = field.String("Bitis Saat", default='12', index=True)
    bitis_dakika = field.String("Bitis Dakika", default='00', index=True)
    derslik_durum = field.Integer("Durum", choices=DERSLIK_DURUMU, index=True)

