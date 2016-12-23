# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Ünvan Sorgula

Hitap üzerinden personelin ünvan bilgilerinin sorgulamasını yapar.

"""

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetUnvanGetir(HITAPSorgula):
    """
    HITAP Sorgulama servisinden kalıtılmış Ünvan Bilgisi Sorgulama servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            bean_name (str): Hitap'tan gelen bean nesnesinin adı
            service_dict (dict): Hitap servisinden gelen kayıtların alanları,
                    ``HizmetUnvan`` modelinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetUnvanSorgula'
        self.bean_name = 'HizmetUnvanServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'kayit_no': 'kayitNo',
                'unvan_kod': 'unvanKod',
                'unvan_tarihi': 'unvanTarihi',
                'unvan_bitis_tarihi': 'unvanBitisTarihi',
                'hizmet_sinifi': 'hizmetSinifi',
                'asil_vekil': 'asilVekil',
                'atama_sekli': 'atamaSekli',
                'fhz_orani': 'fhzOrani',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['unvan_tarihi', 'unvan_bitis_tarihi', 'kurum_onay_tarihi'],
            'required_fields': ['tckn']
        }
        super(HizmetUnvanGetir, self).handle()
