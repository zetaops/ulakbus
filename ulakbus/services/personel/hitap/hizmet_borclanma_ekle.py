# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Borclanma Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetBorclanmaEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Borçlanma Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetBorclanmaInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetBorclanmaInsert'

        self.service_dict = {
            'fields': {
                'tckn': self.request.payload['tckn'],
                'ad': self.request.payload['ad'],
                'soyad': self.request.payload['soyad'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'gunSayisi': self.request.payload['gun_sayisi'],
                'odenenMiktar': self.request.payload['odenen_miktar'],
                'toplamTutar': self.request.payload['toplam_tutar'],
                'kanunKod': self.request.payload['kanun_kod'],
                'borcNevi': self.request.payload['borc_nevi'],
                'borclanmaTarihi': self.request.payload['borclanma_tarihi'],
                'odemeTarihi': self.request.payload['odeme_tarihi'],
                'derece': self.request.payload['derece'],
                'kademe': self.request.payload['kademe'],
                'ekgosterge': self.request.payload['ekgosterge'],
                'emekliSicil': self.request.payload['emekli_sicil'],
                'calistigiKurum': self.request.payload['calistigi_kurum'],
                'isyeriIl': self.request.payload['isyeri_il'],
                'isyeriIlce': self.request.payload['isyeri_ilce'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'borclanmaTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'kayitNo', 'ad', 'soyad', 'emekliSicil', 'derece', 'kademe',
                                'ekgosterge', 'baslamaTarihi', 'bitisTarihi', 'gunSayisi',
                                'kanunKod', 'borcNevi', 'toplamTutar', 'calistigiKurum', 'isyeriIl',
                                'isyeriIlce',
                                'kurumOnayTarihi']
        }
        super(HizmetBorclanmaEkle, self).handle()
