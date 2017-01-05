# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Açık Süre Senkronizasyon

Personelin Hitap'taki açık süre hizmet bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetAcikSure


class HizmetAcikSureSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış
    Açık Süre Hizmet Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'sorgula_service': 'hizmet-acik-sure-getir',
        'model': HizmetAcikSure
    }
