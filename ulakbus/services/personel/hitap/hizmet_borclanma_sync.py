# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Borçlanma Senkronizasyon

Personelin Hitap'taki borçlanma bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetBorclanma


class HizmetBorclanmaSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Borçlanma Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``HizmetBorclanma`` modeli

        """

        self.sorgula_service = 'hizmet-borclanma-getir.hizmet-borclanma-getir'
        self.model = HizmetBorclanma

        super(HizmetBorclanmaSync, self).handle()
