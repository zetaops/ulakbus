# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP IHS Ekle

Hitap'a personelin IHS bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetIhsEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet IHS Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetIHSInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetIHSInsert'
        hizmet_ihs = HizmetIHS.objects.get(key)
        self.service_dict = {
            'fields': {
                'tckn': self.request.payload['tckn'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'ihzNevi': self.request.payload['ihz_nevi'],
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi'],
            'required_fields': ['tckn', 'baslama_tarihi', 'bitis_tarihi', 'ihzNevi']
        }
        super(HizmetIhsEkle, self).handle()
