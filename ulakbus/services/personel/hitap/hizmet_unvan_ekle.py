# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Unvan Ekle

Hitap'a personelin Unvan bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle
from ulakbus.models.hitap import HizmetUnvan


class HizmetUnvanEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Unvan Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetUnvan'' modelinden gelen kayıtların alanları,
                    HizmetUnvanInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetUnvanInsert'
        hizmet_unvan = HizmetUnvan.objects.get(key)
        self.service_dict = {
            'fields': {
                'asilVekil': hizmet_unvan.asil_vekil,
                'atamaSekli': hizmet_unvan.atama_sekli,
                'hizmetSinifi': hizmet_unvan.hizmet_sinifi,
                'tckn': hizmet_unvan.tckn,
                'unvanKod': hizmet_unvan.unvan_kod,
                'unvanTarihi': hizmet_unvan.unvan_tarihi,
                'unvanBitisTarihi': hizmet_unvan.unvan_bitis_tarihi,
                'kurumOnayTarihi': hizmet_unvan.kurum_onay_tarihi,
                'fhzOrani': hizmet_unvan.fhz_orani
            },
            'date_filter': ['unvanTarihi', 'unvanBitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetUnvanEkle, self).handle()
