# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Istisnai Ilgi Sil

Hitap'da personelin Hizmet Istisnai Ilgi bilgilerinin silinmesi sağlayan class.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetIstisnaiIlgiSil(ZatoHitapService):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Cetveli Bilgisi Silme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'hizmetIstisnaiIlgiDelete',
        'fields': {
            'tckn': 'tckn',
            'kayitNo': 'kayit_no'
        },
        'required_fields': ['tckn', 'kayit_no']
    }
