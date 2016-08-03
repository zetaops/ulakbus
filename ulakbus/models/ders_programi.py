# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field
from .buildings_rooms import Room
from .auth import Unit
from .ogrenci import Okutman

UYGUNLUK_DURUMU = [
    (1, "Uygun"),
    (2, "Mümkünse Uygun Değil"),
    (3, "Kesinlikle Uygun Değil")
]

HAFTA_ICI_GUNLER = [
    (1, "Pazartesi"),
    (2, "Salı"),
    (3, "Çarşamba"),
    (4, "Perşembe"),
    (5, "Cuma")
]

HAFTA_SONU_GUNLER = [
    (6, "Cumartesi"),
    (7, "Pazar")
]

DERSLIK_DURUMU = [
    (1, 'Herkese Açık'),
    (2, 'Bölüme Ait'),
    (3, 'Herkese Kapalı')
]

GUN_DILIMI = [
    (1, 'Sabah'),
    (2, 'Öğle'),
    (3, 'Akşam')
]

HAFTA = HAFTA_ICI_GUNLER + HAFTA_SONU_GUNLER

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
        unique_together = [('derslik', 'gun', 'baslangic_saat', 'baslangic_dakika', 'bitis_saat', 'bitis_dakika')]
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
                                         dict(DERSLIK_DURUMU)[self.derslik_durum])
