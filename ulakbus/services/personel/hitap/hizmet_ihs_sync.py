# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Senkronizasyon

Personelin Hitap'taki itibari hizmet süresi zammı bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetIHS


class HizmetIHSSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış İtibari Hizmet Süresi Zammı
    Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``HizmetIHS`` modeli

        """

        self.sorgula_service = 'hizmet-ihs-getir.hizmet-ihs-getir'
        self.model = HizmetIHS

        super(HizmetIHSSync, self).handle()
