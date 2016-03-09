# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Tazminat Guncelle

Hitap'a personelin Tazminat bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetTazminatGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Tazminat Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetTazminatUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetTazminatUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload['kayit_no'],
                'gorev': self.request.payload['gorev'],
                'kadrosuzluk': self.request.payload['kadrosuzluk'],
                'makam': self.request.payload['makam'],
                'tckn': self.request.payload['tckn'],
                'temsil': self.request.payload['temsil'],
                'unvanKod': self.request.payload['unvan_kod'],
                'tazminatTarihi': self.request.payload['tazminat_tarihi'],
                'tazminatBitisTarihi': self.request.payload['tazminat_bitis_tarihi'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['tazminatTarihi', 'tazminatBitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['kayitNo', 'tckn', 'unvanKod', 'tazminatTarihi', 'kurumOnayTarihi']
        }
        super(HizmetTazminatGuncelle, self).handle()
