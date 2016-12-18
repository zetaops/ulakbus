# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Nufus Guncelle

Hitap'a personelin Nufus bilgilerinin guncellenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetNufusGuncelle(HITAPGuncelle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Nufus Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): : Request yoluyla gelen kayıtlar,
                    HizmetNufusUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetNufusUpdate'
        self.service_dict = {
            'fields': {
                'ad': self.request.payload.get('ad', ''),
                'cinsiyet': self.request.payload.get('cinsiyet', ''),
                'dogumTarihi': self.request.payload.get('dogum_tarihi', ''),
                'durum': self.request.payload.get('durum', ''),
                'emekliSicilNo': self.request.payload.get('emekli_sicil_no', ''),
                'ilkSoyad': self.request.payload.get('ilk_soy_ad', ''),
                'kurumSicili': self.request.payload.get('kurum_sicil', ''),
                'maluliyetKod': self.request.payload.get('maluliyet_kod', ''),
                'memuriyetBaslamaTarihi': self.request.payload.get('memuriyet_baslama_tarihi', ''),
                'sebep': self.request.payload.get('sebep', ''),
                'soyad': self.request.payload.get('soyad', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'aciklama': self.request.payload.get('aciklama', ''),
                'yetkiSeviyesi': self.request.payload.get('yetki_seviyesi', ''),
                'kurumaBaslamaTarihi': self.request.payload.get('kuruma_baslama_tarihi', ''),
                'gorevTarihi6495': self.request.payload.get('gorev_tarihi_6495', ''),
                'emekliSicil6495': self.request.payload.get('emekli_sicil_6495', '')
            },
            'date_filter': ['dogumTarihi', 'memuriyetBaslamaTarihi', 'kurumaBaslamaTarihi'],
            'required_fields': ['tckn', 'ad', 'soyad', 'dogumTarihi', 'cinsiyet', 'emekliSicilNo',
                                'memuriyetBaslamaTarihi', 'durum', 'kurumSicili', 'maluliyetKod',
                                'sebep', 'yetkiSeviyesi']

        }
        super(HizmetNufusGuncelle, self).handle()
