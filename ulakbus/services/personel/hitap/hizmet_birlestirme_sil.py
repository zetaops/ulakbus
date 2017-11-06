# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Birleştirme Sil

Hitap'da personelin Hizmet Birleştirme bilgilerinin silinmesi sağlayan class.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetBirlestirmeSil(ZatoHitapService):
    """
    HITAP Silme servisinden kalıtılmış Hizmet Birleştirme Bilgisi Silme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetBirlestirmeDelete',
        'fields': {
            'tckn': 'tckn',
            'kayitNo': 'kayit_no'
        },
        'required_fields': ['tckn', 'kayit_no']
    }
