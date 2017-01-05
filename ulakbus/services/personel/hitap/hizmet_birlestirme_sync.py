# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Birleştirme Senkronizasyon

Personelin Hitap'taki hizmet birleştirme bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetBirlestirme


class HizmetBirlestirmeSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Hizmet Birleştirme Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'sorgula_service': 'hizmet-birlestirme-getir',
        'model': HizmetBirlestirme
    }
