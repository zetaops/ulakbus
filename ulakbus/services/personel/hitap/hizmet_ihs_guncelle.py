# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Guncelle

Hitap'a personelin IHS bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetIhsGuncelle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetIHSUpdate',
        'fields': {
            'ihzID': 'kayit_no',
            'tckn': 'tckn',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'ihzNevi': 'ihz_nevi',
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi'],
        'required_fields': ['tckn', 'ihzID', 'baslamaTarihi', 'bitisTarihi', 'ihzNevi']
    }
