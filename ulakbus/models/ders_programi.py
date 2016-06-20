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

HAFTA_ICI_ZAMAN_DILIMLERI = [
    (1, "08:00 - 12:00"),
    (2, "13:00 - 17:00"),
    (3, "17:00 - 21:00")
]

HAFTA_SONU_ZAMAN_DILIMLERI = HAFTA_ICI_ZAMAN_DILIMLERI

class OgElemaniZamanPlani(Model):
    """

        pass

    """

    class Meta:
        app = 'Ogrenci'
        verbose_name = 'Ogretim Elemani Zaman Kaydi'
        verbose_name_plural = 'Ogretim Elemanlari Zaman Kaydi'
        unique_together = [('okutman', 'bolum')]


    okutman = Okutman(unique=True)
    bolum = Unit(unique=True)
    toplam_ders_saati = field.Integer("Ogretim Elemani Toplam Ders Saati", index=True)

    class ZamanCetveli(ListNode):
        class Meta:
            unique_together = [('gun', 'zaman_araligi')]
        gun = field.Integer(choices=HAFTA)
        zaman_araligi = field.Integer(choices=HAFTA_ICI_ZAMAN_DILIMLERI)
        durum = field.Integer(choices=UYGUNLUK_DURUMU)
















