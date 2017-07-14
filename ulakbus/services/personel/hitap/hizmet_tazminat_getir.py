# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Sorgula

Hitap üzerinden personelin tazminat bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetTazminatGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Tazminat Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetTazminatSorgula',
        'bean_name': 'HizmetTazminatServisBean',
        'fields': {
            'tckn': 'tckn',
            'kayit_no': 'kayitNo',
            'unvan_kod': 'unvanKod',
            'makam': 'makam',
            'gorev': 'gorev',
            'temsil': 'temsil',
            'tazminat_tarihi': 'tazminatTarihi',
            'tazminat_bitis_tarihi': 'tazminatBitisTarihi',
            'kadrosuzluk': 'kadrosuzluk',
            'kurum_onay_tarihi': 'kurumOnayTarihi',
        },
        'date_filter': ['tazminat_tarihi', 'tazminat_bitis_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['tckn']
    }
