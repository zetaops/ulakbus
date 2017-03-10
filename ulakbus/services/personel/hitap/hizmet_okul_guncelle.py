# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Guncelle

Hitap'a personelin Okul bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetOkulGuncelle(ZatoHitapService):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Okul Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetOkulUpdate',
        'fields': {
            'bolum': 'bolum',
            'kayitNo': 'kayit_no',
            'mezuniyetTarihi': 'mezuniyet_tarihi',
            'ogrenimDurumu': 'ogrenim_durumu',
            'ogrenimSuresi': 'ogrenim_suresi',
            'okulAd': 'okul_ad',
            'tckn': 'tckn',
            'denklikTarihi': 'denklik_tarihi',
            'ogrenimYer': 'ogrenim_yeri',
            'denklikBolum': 'denklik_bolum',
            'denklikOkul': 'denklik_okul',
            'hazirlik': 'hazirlik',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['kayitNo', 'tckn', 'ogrenimDurumu', 'mezuniyetTarihi',
                            'ogrenimSuresi', 'hazirlik', 'kurumOnayTarihi']
    }
