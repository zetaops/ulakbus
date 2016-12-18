# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Unvan Guncelle

Hitap'a personelin Unvan bilgilerinin guncellenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetUnvanGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Unvan Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetUnvanUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetUnvanUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload.get('kayit_no', ''),
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
            'required_fields': ['kayitNo', 'tckn', 'unvanKod', 'unvanTarihi', 'hizmetSinifi',
                                'asilVekil', 'atamaSekli', 'kurumOnayTarihi']
        }
        super(HizmetUnvanGuncelle, self).handle()
