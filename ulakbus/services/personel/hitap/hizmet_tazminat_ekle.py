# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Ekle

Hitap'a personelin Tazminat bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetTazminatEkle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Tazminat Bilgi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetTazminatInsert',
        'fields': {
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
        'long_to_string': ['kayit_no'],
        'required_fields': ['tckn', 'unvanKod', 'tazminatTarihi', 'kurumOnayTarihi']
    }
