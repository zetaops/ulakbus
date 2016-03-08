# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Kurs Ekle

Hitap'a personelin kurs bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetKursEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Kurs Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetKursInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları ve servis tarafında gerekli olan
                    alanlar listede tutulmaktadır.
        """

        self.service_name = 'HizmetKursInsert'
        self.service_dict = {
            'fields': {
                'tckn': self.request.payload['tckn'],
                'kursOgrenimSuresi': self.request.payload['kurs_ogrenim_suresi'],
                'mezuniyetTarihi': self.request.payload['mezuniyet_tarihi'],
                'kursNevi': self.request.payload['kurs_nevi'],
                'bolumAd': self.request.payload['bolum_ad'],
                'okulAd': self.request.payload['okul_ad'],
                'ogrenimYeri': self.request.payload['ogrenim_yeri'],
                'denklikTarihi': self.request.payload['denklik_tarihi'],
                'denklikOkul': self.request.payload['denklik_okulu'],
                'denklikBolum': self.request.payload['denklik_bolum'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['mezuniyetTarihi', 'denklikTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'kursOgrenimSuresi', 'mezuniyetTarihi', 'kursNevi',
                                'okulAd', 'kurumOnayTarihi']
        }
        super(HizmetKursEkle, self).handle()
