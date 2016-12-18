# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Okul Ekle

Hitap'a personelin Okul bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetOkulEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Okul Bilgi Ekleme servisi

    """
    HAS_CHANNEL = True

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
                'bolum': self.request.payload.get('bolum', ''),
                'kayitNo': self.request.payload.get('kayit_no', ''),
                'mezuniyetTarihi': self.request.payload.get('mezuniyet_tarihi', ''),
                'ogrenimDurumu': self.request.payload.get('ogrenim_durumu', ''),
                'ogrenimSuresi': self.request.payload.get('ogrenim_suresi', ''),
                'okulAd': self.request.payload.get('okul_ad', ''),
                'tckn': self.request.payload.get('tckn', ''),
                'denklikTarihi': self.request.payload.get('denklik_tarihi', ''),
                'ogrenimYer': self.request.payload.get('ogrenim_yeri', ''),
                'denklikBolum': self.request.payload.get('denklik_bolum', ''),
                'denklikOkul': self.request.payload.get('denklik_okul', ''),
                'hazirlik': self.request.payload.get('hazirlik', ''),
                'kurumOnayTarihi': self.request.payload.get('kurum_onay_tarihi', '')
            },
            'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'ogrenimDurumu', 'mezuniyetTarihi', 'ogrenimSuresi',
                                'hazirlik', 'kurumOnayTarihi']
        }
        super(HizmetOkulEkle, self).handle()
