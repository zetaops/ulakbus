# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Istisnai Ilgi Ekle

Hitap'a personelin Istisnai Ilgi bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetIstisnaiIlgiEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Istisnai Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtların alanları,
                    hizmetIstisnaiIlgiInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'hizmetIstisnaiIlgiInsert'
        hizmet_is_ilgi = HizmetIstisnaiIlgi.objects.get(key)
        self.service_dict = {
            'fields': {
                'tckn': self.request.payload['tckn'],
                'istisnaiIlgiNevi': self.request.payload['istisnai_ilgi_nevi'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'gunSayisi': self.request.payload['gun_sayisi'],
                'khaDurum': self.request.payload['kha_durum'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'istisnaiIlgiNevi', 'baslamaTarihi', 'bitisTarihi',
                                'gunSayisi', 'khaDurum', 'kurumOnayTarihi']
        }
        super(HizmetIstisnaiIlgiEkle, self).handle()
