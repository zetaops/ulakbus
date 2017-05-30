# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Sorgula

Hitap üzerinden personelin okul bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetOkulGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Okul Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetOkulSorgula',
        'bean_name': 'HizmetEgitimOkulServisBean',
        'fields': {
            'tckn': 'tckn',
            'kayit_no': 'kayitNo',
            'ogrenim_durumu': 'ogrenimDurumu',
            'mezuniyet_tarihi': 'mezuniyetTarihi',
            'okul_ad': 'okulAd',
            'bolum': 'bolum',
            'ogrenim_yeri': 'ogrenimYer',
            'denklik_tarihi': 'denklikTarihi',
            'denklik_okul': 'denklikOkul',
            'denklik_bolum': 'denklikBolum',
            'ogrenim_suresi': 'ogrenimSuresi',
            'hazirlik': 'hazirlik',
            'kurum_onay_tarihi': 'kurumOnayTarihi'
        },
        'date_filter': ['mezuniyet_tarihi', 'denklik_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['tckn']
    }
