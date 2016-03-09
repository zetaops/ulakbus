# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Birleştirme Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetBirlestirmeEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Birlestirme Bilgisi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetBirlestirmeInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        self.service_name = 'HizmetBirlestirmeInsert'

        self.service_dict = {
            'fields': {
                'tckn': self.request.payload['tckn'],
                'sgkNevi': self.request.payload['sgk_nevi'],
                'sgkSicilNo': self.request.payload['sgk_sicil_no'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'kamuIsyeriAd': self.request.payload['kamu_isyeri_ad'],
                'ozelIsyeriAd': self.request.payload['ozel_isyeri_ad'],
                'bagKurMeslek': self.request.payload['bag_kur_meslek'],
                'ulkeKod': self.request.payload['ulke_kod'],
                'bankaSandikKod': self.request.payload['banka_sandik_kod'],
                'kidemTazminatOdemeDurumu': self.request.payload['kidem_tazminat_odeme_durumu'],
                'ayrilmaNedeni': self.request.payload['ayrilma_nedeni'],
                'sure': self.request.payload['sure'],
                'khaDurum': self.request.payload['kha_durum'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['tckn', 'sgkNevi', 'sgkSicilNo', 'baslamaTarihi',
                                'bitisTarihi', 'sure', 'kurumOnayTarihi']
        }
        super(HizmetBirlestirmeEkle, self).handle()
