# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Mahkeme Senkronizasyon

Personelin Hitap'taki mahkeme bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetMahkeme


class HizmetMahkemeSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Mahkeme Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``HizmetMahkeme`` modeli

        """

        self.sorgula_service = 'hizmet-mahkeme-getir.hizmet-mahkeme-getir'
        self.model = HizmetMahkeme

        super(HizmetMahkemeSync, self).handle()
