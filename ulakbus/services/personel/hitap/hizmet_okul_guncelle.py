# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Guncelle

Hitap'a personelin Okul bilgilerinin guncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetOkulGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Okul Bilgi Guncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetOkulUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.

        """

        self.service_name = 'HizmetOkulUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload['kayit_no'],
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
            'required_fields': ['kayitNo', 'tckn', 'ogrenimDurumu', 'mezuniyetTarihi',
                                'ogrenimSuresi', 'hazirlik', 'kurumOnayTarihi']
        }
        super(HizmetOkulGuncelle, self).handle()
