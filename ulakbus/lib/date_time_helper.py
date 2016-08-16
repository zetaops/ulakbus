# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Ali Riza Keles'

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

GUN_DILIMI = [
    (1, 'Sabah'),
    (2, 'Öğle'),
    (3, 'Akşam')
]

HAFTA = HAFTA_ICI_GUNLER + HAFTA_SONU_GUNLER

GUN_LISTESI = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

AYLAR = [(1, 'Ocak'), (2, 'Şubat'), (3, 'Mart'), (4, 'Nisan'),
         (5, 'Mayıs'), (6, 'Haziran'), (7, 'Temmuz'), (8, 'Ağustos'),
         (9, 'Eylül'), (10, 'Ekim'), (11, 'Kasım'), (12, 'Aralık')]


def map_sinav_etkinlik_hafta_gunleri(sinavlar):
    """
    Sinav nesnelerini tarihlerine gore haftanin gunlerine dagitir.

    Haftanin gunlerinin key olarak kullanildigi bir dict uretir.

    ..code_block
    {
        1: ["Matematik Ara Sinav -1", "Fizik Ara Sinav -1"],
        2: ["Edebiyat", ]
        ...

    }

    Args:
         sinavlar (list): sinav etkinligi objeleri listesi

    Returns:
        (dict)
    """
    r = {}
    for e in sinavlar:
        weekday = e.tarih.isoweekday()
        etkinlik_listesi = r.get(weekday, [])
        etkinlik_listesi.append(e.__unicode__())
        r[weekday] = etkinlik_listesi
    return r
