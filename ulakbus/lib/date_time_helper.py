# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import timedelta, date
import calendar

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

def zaman_araligi(baslangic, bitis):
    """
    Verilen iki tarih arasinda kalan tarihleri
    donduren method.

    Args:
        baslangic: Date 02.04.2016
        bitis: Date 04.04.2016

    Returns:
        [02.04.2016,03.04.2016,04.04.2016]

    """
    for n in range(int((bitis - baslangic).days) + 1):
        yield baslangic + timedelta(n)

def resmi_tatil_gunleri_getir(birim_unit, yil, ay):
    from ulakbus.models.ogrenci import Takvim, Donem
    from ulakbus.lib.common import get_akademik_takvim

    baslangic,bitis = yil_ve_aya_gore_ilk_son_gun(yil,ay)
    resmi_tatil_list = []
    donem_list = Donem.takvim_ayina_rastlayan_donemler(yil,ay)
    for donem in donem_list:
        akademik_takvim = get_akademik_takvim(birim_unit, donem.ogretim_yili)
        tatil_list = []
        for resmi_tatil in Takvim.objects.filter(akademik_takvim=akademik_takvim,
                                                 resmi_tatil=True,baslangic__gte=baslangic,
                                                 bitis__lte=bitis):
            for gun in zaman_araligi(resmi_tatil.baslangic, resmi_tatil.bitis):
                    tatil_list.append(gun.day)
        resmi_tatil_list.append(tatil_list)

    return resmi_tatil_list

def yil_ve_aya_gore_ilk_son_gun(yil,ay):

    baslangic = date(yil, ay, 1)
    ay_sonu = calendar.monthrange(yil, ay)[1]
    bitis = date(yil,ay,ay_sonu)

    return (baslangic,bitis)