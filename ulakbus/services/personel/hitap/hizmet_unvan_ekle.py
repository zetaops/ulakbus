# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Unvan Ekle

Hitap'a personelin Unvan bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetUnvanEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Unvan Bilgi Ekleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetUnvanInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetUnvanInsert'
        self.service_dict = {
            'fields': {
                'asilVekil': self.request.payload.get('asil_vekil', ''),
                'atamaSekli': self.request.payload.get('atama_sekli', ''),
                'hizmetSinifi': self.request.payload.get('hizmet_sinifi', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'unvanKod': self.request.payload.get('unvan_kod', ''),
                'unvanTarihi': self.request.payload.get('unvan_tarihi', ''),
                'unvanBitisTarihi': self.request.payload.get('unvan_bitis_tarihi', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', ''),
                'fhzOrani': self.request.payload.get('fhz_orani', '')
            },
            'date_filter': ['unvanTarihi', 'unvanBitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'unvanKod', 'unvanTarihi', 'hizmetSinifi', 'asilVekil',
                                'atamaSekli', 'kurumOnayTarihi']

        }
        super(HizmetUnvanEkle, self).handle()
