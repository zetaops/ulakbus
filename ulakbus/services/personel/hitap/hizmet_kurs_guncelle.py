# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Guncelle

Hitap'a personelin Kurs bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetKursGuncelle(ZatoHitapService):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Kurs Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetKursUpdate',
        'fields': {
            'kayitNo': 'kayit_no',
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
        'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['tckn', 'kayitNo', 'kursOgrenimSuresi', 'mezuniyetTarihi',
                            'kursNevi', 'okulAd', 'kurumOnayTarihi']
    }
