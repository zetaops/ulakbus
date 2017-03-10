# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Guncelle

Hitap'a personelin Tazminat bilgilerinin guncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetTazminatGuncelle(ZatoHitapService):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Tazminat Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetTazminatUpdate',
        'fields': {
            'kayitNo': 'kayit_no',
            'gorev': 'gorev',
            'kadrosuzluk': 'kadrosuzluk',
            'makam': 'makam',
            'tckn': 'tckn',
            'temsil': 'temsil',
            'unvanKod': 'unvan_kod',
            'tazminatTarihi': 'tazminat_tarihi',
            'tazminatBitisTarihi': 'tazminat_bitis_tarihi',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['tazminat_tarihi', 'tazminat_bitis_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['kayitNo', 'tckn', 'unvanKod', 'tazminatTarihi', 'kurumOnayTarihi']
    }
