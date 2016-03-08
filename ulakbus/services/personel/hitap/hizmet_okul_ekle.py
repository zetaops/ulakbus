# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Ekle

Hitap'a personelin Okul bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetOkulEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Okul Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetOkulInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetOkulInsert'
        self.service_dict = {
            'fields': {
                'bolum': self.request.payload['bolum'],
                'kayitNo': self.request.payload['kayit_no'],
                'mezuniyetTarihi': self.request.payload['mezuniyet_tarihi'],
                'ogrenimDurumu': self.request.payload['ogrenim_durumu'],
                'ogrenimSuresi': self.request.payload['ogrenim_suresi'],
                'okulAd': self.request.payload['okul_ad'],
                'tckn': self.request.payload['tckn'],
                'denklikTarihi': self.request.payload['denklik_tarihi'],
                'ogrenimYer': self.request.payload['ogrenim_yeri'],
                'denklikBolum': self.request.payload['denklik_bolum'],
                'denklikOkul': self.request.payload['denklik_okul'],
                'hazirlik': self.request.payload['hazirlik'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'ogrenimDurumu', 'mezuniyetTarihi', 'ogrenimSuresi',
                                'hazirlik', 'kurumOnayTarihi']
        }
        super(HizmetOkulEkle, self).handle()
