# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Kurs Sil

Hitap'da personelin Hizmet Kurs bilgilerinin silinmesi sağlayan class.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetKursSil(ZatoHitapService):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Kurs Bilgisi Silme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'fields': {
            'tckn': 'tckn',
            'kayitNo': 'kayit_no'
        },
        'service_name': 'HizmetKursDelete',
        'required_fields': ['tckn', 'kayitNo']
    }
