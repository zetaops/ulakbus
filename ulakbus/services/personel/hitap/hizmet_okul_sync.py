# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Senkronizasyon

Personelin Hitap'taki okul bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetOkul


class HizmetOkulSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Okul Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'sorgula_service': 'hizmet-okul-getir',
        'model': HizmetOkul
    }
