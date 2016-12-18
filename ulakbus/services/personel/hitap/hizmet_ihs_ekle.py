# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Ekle

Hitap'a personelin IHS bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetIhsEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetIHSInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.

        """

        self.service_name = 'HizmetIHSInsert'
        self.service_dict = {
            'fields': {
                'tckn': self.request.payload.get('tckn', ''),
                'baslamaTarihi': self.request.payload.get('baslama_tarihi', ''),
                'bitisTarihi': self.request.payload.get('bitis_tarihi', ''),
                'ihzNevi': self.request.payload.get('ihz_nevi', '')
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi'],
            'required_fields': ['tckn', 'baslamaTarihi', 'bitisTarihi', 'ihzNevi']
        }
        super(HizmetIhsEkle, self).handle()
