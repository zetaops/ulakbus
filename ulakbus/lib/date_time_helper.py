# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

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


def _liste_hazirla(fn, keep_fn=False):
    """Babel'ın `get_day_names` ve `get_month_names` özelliklerini Ulakbus'e uyarlar.

    Babel'ın `get_day_names` ve `get_month_names` methodları, gün ve ayları 0-indeksli
    sözlükler olarak veriyor. Ancak uygulamanın bir çok yerinde `HAFTA` ve `AYLAR`
    listelerinin 1-indeksli tuple'lar içeren bir liste olması bekleniyor. Ayrıca, gün
    ve ay isimlerinin bakılmasının, isimler kullanıcıya gönderilmeden hemen önce
    yapılması gerekli ki kullanıcının seçtiği tarih tercihine göre gönderilebilsin.

    Bunu sağlamak adına, LazyProxy ile listenin oluşturulması kullanım anına ertelenmiş,
    yardımcı fonksiyon ile de indeksler beklenen sayılara kaydırılmıştır.
    """
    def hazirlik():
        liste = []
        for i, eleman in fn().items():
            liste.append((i + 1, eleman))
        return liste
    if not keep_fn:
        return LazyProxy(hazirlik, enable_cache=False)
    else:
        return hazirlik

HAFTA = _liste_hazirla(get_day_names)
gun_listele = _liste_hazirla(get_day_names, keep_fn=True)

AYLAR = _liste_hazirla(get_month_names)
ay_listele = _liste_hazirla(get_month_names, keep_fn=True)


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
