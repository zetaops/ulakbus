# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Sorgula

Hitap üzerinden personelin itibari hizmet süresi zammı bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetIHSGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış IHS Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetIHSSorgula',
        'bean_name': 'HizmetIHSServisBean',
        'fields': {
            'tckn': 'tckn',
            'kayit_no': 'ihzID',
            'baslama_tarihi': 'baslamaTarihi',
            'bitis_tarihi': 'bitisTarihi',
            'ihz_nevi': 'ihzNevi'
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi'],
        'required_fields': ['tckn']
    }
