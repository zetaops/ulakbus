# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Nufus Ekle

Hitap'a personelin Nufus bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetNufusEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Nufus Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetNufusInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetNufusInsert'
        self.service_dict = {
            'fields': {
                'ad': self.request.payload['ad'],
                'cinsiyet': self.request.payload['cinsiyet'],
                'dogumTarihi': self.request.payload['dogum_tarihi'],
                'durum': self.request.payload['durum'],
                'emekliSicilNo': self.request.payload['emekli_sicil_no'],
                'ilkSoyad': self.request.payload['ilk_soy_ad'],
                'kurumSicili': self.request.payload['kurum_sicil'],
                'maluliyetKod': self.request.payload['maluliyet_kod'],
                'memuriyetBaslamaTarihi': self.request.payload['memuriyet_baslama_tarihi'],
                'sebep': self.request.payload['sebep'],
                'soyad': self.request.payload['soyad'],
                'tckn': self.request.payload['tckn'],
                'aciklama': self.request.payload['aciklama'],
                'yetkiSeviyesi': self.request.payload['yetki_seviyesi'],
                'kurumaBaslamaTarihi': self.request.payload['kuruma_baslama_tarihi'],
                'gorevTarihi6495': self.request.payload['gorev_tarihi_6495'],
                'emekliSicil6495': self.request.payload['emekli_sicil_6495']
            },
            'date_filter': ['dogumTarihi', 'memuriyetBaslamaTarihi', 'kurumaBaslamaTarihi'],
            'required_fields': ['tckn', 'ad', 'soyad', 'dogumTarihi', 'cinsiyet', 'emekliSicilNo',
                                'memuriyetBaslamaTarihi', 'durum', 'kurumSicili', 'maluliyetKod',
                                'sebep', 'yetkiSeviyesi']
        }
        super(HizmetNufusEkle, self).handle()
