# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP İstisnai İlgi Senkronizasyon

Personelin Hitap'taki istisnai ilgi bilgilerinin
yereldeki kayıtlarla senkronizasyonunu yapar.

Note:
    Bu servis, sorgulama servisindeki hatadan dolayı çalışmamaktadır.
    Açıklama için ilgili birimlere başvuruldu, yanıt bekleniyor.

"""

from ulakbus.services.personel.hitap.hitap_sync import HITAPSync
from ulakbus.models.hitap.hitap import HizmetIstisnaiIlgi


class HizmetIstisnaiIlgiSync(HITAPSync):
    """
    HITAP Sync servisinden kalıtılmış İstisnai İlgi Bilgisi Senkronizasyon servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            sorgula_service (str): İlgili Hitap sorgu servisinin adı
            model (Model): Hitap'taki kaydın yereldeki karşılığı olan
                        ``HizmetIstisnaiIlgi`` modeli

        """

        self.sorgula_service = 'hizmet-istisnai-ilgi-getir.hizmet-istisnai-ilgi-getir'
        self.model = HizmetIstisnaiIlgi

        super(HizmetIstisnaiIlgiSync, self).handle()
