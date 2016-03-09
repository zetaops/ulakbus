# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Mahkeme Guncelle

Hitap'a personelin Mahkeme bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetMahkemeGuncelle(HITAPGuncelle):
    """HITAP Guncelleme servisinden kalıtılmış Hizmet Mahkeme Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetMahkemeUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetMahkemeUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload['kayit_no'],
                'tckn': self.request.payload['tckn'],
                'mahkemeAd': self.request.payload['mahkeme_ad'],
                'sebep': self.request.payload['sebep'],
                'kararTarihi': self.request.payload['karar_tarihi'],
                'kararSayisi': self.request.payload['karar_sayisi'],
                'kesinlesmeTarihi': self.request.payload['kesinlesme_tarihi'],
                'asilDogumTarihi': self.request.payload['asil_dogum_tarihi'],
                'tashihDogumTarihi': self.request.payload['tashih_dogum_tarihi'],
                'gecerliDogumTarihi': self.request.payload['gecerli_dogum_tarihi'],
                'asilAd': self.request.payload['asil_ad'],
                'tashihAd': self.request.payload['tashih_ad'],
                'asilSoyad': self.request.payload['asil_soyad'],
                'tashihSoyad': self.request.payload['tashih_soyad'],
                'aciklama': self.request.payload['aciklama'],
                'gunSayisi': self.request.payload['gun_sayisi'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['kesinlesmeTarihi', 'asilDogumTarihi', 'tashihDogumTarihi',
                            'gecerliDogumTarihi', 'kurumOnayTarihi'],
            'required_fields': ['kayitNo', 'tckn', 'mahkemeAd', 'sebep', 'kararTarihi', 'kararSayisi',
                                'kurumOnayTarihi']

        }
        super(HizmetMahkemeGuncelle, self).handle()
