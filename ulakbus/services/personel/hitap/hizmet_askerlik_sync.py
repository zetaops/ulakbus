# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Askerlik Senkronizasyon

Personelin Hitap'taki askerlik bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import AskerlikKayitlari


class HizmetAskerlikSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış Askerlik Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``AskerlikKayitlari`` modeli

        """

        self.sorgula_service = 'hizmet-askerlik-getir.hizmet-askerlik-getir'
        self.model = AskerlikKayitlari

        super(HizmetAskerlikSync, self).handle()
