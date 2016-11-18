# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict
from datetime import timedelta, date
import calendar
from zengine.lib.translation import gettext_lazy, gettext as _, LazyProxy, get_day_names, get_month_names

__author__ = 'Ali Riza Keles'


def gun_dilimi_listele():
    return [
        (1, _(u'Sabah')),
        (2, _(u'Öğle')),
        (3, _(u'Akşam')),
    ]


def _liste_hazirla(fn, make_choices=False):
    """Babel'ın `get_day_names` ve `get_month_names` özelliklerini Ulakbus'e uyarlar.

    Babel'ın `get_day_names` ve `get_month_names` methodları, gün ve ayları 0-indeksli
    sözlükler olarak veriyor. Ancak uygulamanın bir çok yerinde `HAFTA` ve `AYLAR`
    listelerinin 1-indeksli tuple'lar içeren bir liste olması bekleniyor. Ayrıca, gün
    ve ay isimlerinin bakılmasının, isimler kullanıcıya gönderilmeden hemen önce
    yapılması gerekli ki kullanıcının seçtiği tarih tercihine göre gönderilebilsin.

    Bunu sağlamak adına, LazyProxy ile listenin oluşturulması kullanım anına ertelenmiş,
    yardımcı fonksiyon ile de indeksler beklenen sayılara kaydırılmıştır.
    """
    def choices_title_map():
        liste = []
        for i, eleman in fn().items():
            liste.append({'name': eleman, 'value': i})
        return liste
    if not make_choices:
        return LazyProxy(lambda: fn().items(), enable_cache=False)
    else:
        return choices_title_map


def _get_day_names():
    modified_days = {}
    days = get_day_names().items()
    for i, name in days:
        modified_days[i + 1] = name
    return modified_days


HAFTA = _liste_hazirla(_get_day_names)
gun_listele = _liste_hazirla(_get_day_names, make_choices=True)

AYLAR = _liste_hazirla(get_month_names)
ay_listele = _liste_hazirla(get_month_names, make_choices=True)


def map_etkinlik_hafta_gunleri(etkinlikler):
    """
    Ders ve Sinav Etkinliği  nesnelerini tarihlerine göre haftanın günlerine dağıtır.

    Haftanınn günlerinin key olarak kullanıldığı  bir dict üretir.

    Args:
        etkinlikler(list) : Sinav ya da ders etkinliği objeleri listesi

    Returns:
        dict
    """

    d = defaultdict(list)
    for etkinlik in etkinlikler:
        if hasattr(etkinlik, "tarih"):
            weekday = etkinlik.tarih.isoweekday()
            etkinlik_listesi = d.get(weekday, [])
            etkinlik_listesi.append(etkinlik.__unicode__())
            d[weekday] = etkinlik_listesi
        else:
            weekday = etkinlik.gun
            ders_etkinlikleri = d[weekday]
            ders_etkinlikleri.append(etkinlik.__unicode__())
            d[weekday] = ders_etkinlikleri
    return d


def zaman_araligi(baslangic, bitis):
    """
    Verilen iki tarih arasinda kalan tarihleri
    donduren method.

    Args:
        baslangic (datetime.date): Date 02.04.2016
        bitis (datetime.date): Date 04.04.2016

    Returns:
        (list) [datetime.date(2016, 4, 2), datetime.date(2016, 4, 3), datetime.date(2016, 4, 4)]

    """
    for n in range(int((bitis - baslangic).days) + 1):
        yield baslangic + timedelta(n)


def resmi_tatil_gunleri_getir(birim_unit, yil, ay):
    from ulakbus.models.ogrenci import Takvim, Donem
    from ulakbus.lib.common import get_akademik_takvim

    baslangic, bitis = yil_ve_aya_gore_ilk_ve_son_gun(yil, ay)
    resmi_tatil_list = []
    donem_list = Donem.takvim_ayina_rastlayan_donemler(yil, ay)
    for donem in donem_list:
        akademik_takvim = get_akademik_takvim(birim_unit, donem.ogretim_yili)
        tatil_list = []
        for resmi_tatil in Takvim.objects.filter(akademik_takvim=akademik_takvim,
                                                 resmi_tatil=True, baslangic__gte=baslangic,
                                                 bitis__lte=bitis):
            for gun in zaman_araligi(resmi_tatil.baslangic, resmi_tatil.bitis):
                tatil_list.append(gun.day)
        resmi_tatil_list.append(tatil_list)

    return resmi_tatil_list


def yil_ve_aya_gore_ilk_ve_son_gun(yil, ay):
    ilk = date(yil, ay, 1)
    ayin_ilk_hafta_gunu, ay_sonu = calendar.monthrange(yil, ay)
    son = date(yil, ay, ay_sonu)

    return ilk, son
