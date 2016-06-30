# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Öğrenci Modülü

Bu modül Ulakbüs uygulaması için öğrenci modeli ve öğrenciyle ilişkili data modellerini içerir.

"""
import six

from pyoko import Model, field, ListNode
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

HAFTA = HAFTA_ICI_GUNLER + HAFTA_SONU_GUNLER


class GunZamanDilimleri(Model):
    class Meta:
        unique_together = [('birim', 'gun', 'baslama', 'bitis')]

    birim = Unit("Birim")
    gun = field.Integer("Gun", choices=HAFTA)
    baslama = field.String("Baslama")
    bitis = field.String("Bitis")

    def post_save(self):
        """
        kayit baslama bitis zamani cakisiyor mu?
        """
        pass


class OgElemaniZamanPlani(Model):
    """

        pass

    """

    class Meta:
        app = 'Ogrenci'
        verbose_name = 'Ogretim Elemani Zaman Kaydi'
        verbose_name_plural = 'Ogretim Elemanlari Zaman Kaydi'
        unique_together = [('okutman', 'birim')]

    okutman = Okutman("Okutman")
    birim = Unit("Birim")
    toplam_ders_saati = field.Integer("Ogretim Elemani Toplam Ders Saati", index=True)


class ZamanCetveli(Model):
    class Meta:
        unique_together = [('zaman_dilimi', 'ogretim_elemani_zaman_plani')]

    zaman_dilimi = GunZamanDilimleri("Zaman Dilimi")
    durum = field.Integer(choices=UYGUNLUK_DURUMU)
    ogretim_elemani_zaman_plani = OgElemaniZamanPlani("Ogretim Elemani")
