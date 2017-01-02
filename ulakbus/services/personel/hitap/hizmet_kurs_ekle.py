# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Ekle

Hitap'a personelin kurs bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetKursEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Kurs Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': "HizmetKursInsert",
        'fields': {
            'tckn': 'tckn',
            'kursOgrenimSuresi': 'kurs_ogrenim_suresi',
            'mezuniyetTarihi': 'mezuniyet_tarihi',
            'kursNevi': 'kurs_nevi',
            'bolumAd': 'bolum_ad',
            'okulAd': 'okul_ad',
            'ogrenimYeri': 'ogrenim_yeri',
            'denklikTarihi': 'denklik_tarihi',
            'denklikOkul': 'denklik_okulu',
            'denklikBolum': 'denklik_bolum',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi'],
        'required_fields': ['tckn', 'kursOgrenimSuresi', 'mezuniyetTarihi', 'kursNevi',
                            'okulAd', 'kurumOnayTarihi']
    }

