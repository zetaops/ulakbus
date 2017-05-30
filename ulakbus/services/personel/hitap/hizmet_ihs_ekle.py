# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Ekle

Hitap'a personelin IHS bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetIhsEkle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetIHSInsert',
        'fields': {
            'tckn': 'tckn',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'ihzNevi': 'ihz_nevi'
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi'],
        'long_to_string': ['kayit_no'],
        'required_fields': ['tckn', 'baslamaTarihi', 'bitisTarihi', 'ihzNevi']
    }
