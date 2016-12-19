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

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``HizmetBirlestirme`` modeli

        """

        self.sorgula_service = 'hizmet-birlestirme-getir.hizmet-birlestirme-getir'
        self.model = HizmetBirlestirme

        super(HizmetBirlestirmeSync, self).handle()
