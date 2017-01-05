# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Ünvan Senkronizasyon

Personelin Hitap'taki ünvan bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetUnvan


class HizmetUnvanSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Ünvan Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'sorgula_service': 'hizmet-unvan-getir',
        'model': HizmetUnvan
    }
