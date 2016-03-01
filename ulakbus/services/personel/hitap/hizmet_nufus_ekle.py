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
from ulakbus.models.hitap import NufusKayitlari


class HizmetNufusEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Nufus Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''NufusKayitlari'' modelinden gelen kayıtların alanları,
                    HizmetNufusInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetNufusInsert'
        hizmet_Nufus = NufusKayitlari.objects.get(key)
        self.service_dict = {
            'fields': {
                'ad': hizmet_nufus.ad,
                'cinsiyet': hizmet_nufus.cinsiyet,
                'dogumTarihi': hizmet_nufus.dogum_tarihi,
                'durum': hizmet_nufus.durum,
                'emekliSicilNo': hizmet_nufus.emekli_sicil_no,
                'ilkSoyad': hizmet_nufus.ilk_soy_ad,
                'kurumSicili': hizmet_nufus.kurum_sicil,
                'maluliyetKod': hizmet_nufus.maluliyet_kod,
                'memuriyetBaslamaTarihi': hizmet_nufus.memuriyet_baslama_tarihi,
                'sebep': hizmet_nufus.sebep,
                'soyad': hizmet_nufus.soyad,
                'tckn': hizmet_nufus.tckn,
                'aciklama': hizmet_nufus.aciklama,
                'yetkiSeviyesi': hizmet_nufus.yetki_seviyesi,
                'kurumaBaslamaTarihi': hizmet_nufus.kuruma_baslama_tarihi,
                'gorevTarihi6495': hizmet_nufus.gorev_tarihi_6495,
                'emekliSicil6495': hizmet_nufus.emekli_sicil_6495
            },
            'date_filter': ['dogumTarihi', 'memuriyetBaslamaTarihi', 'kurumaBaslamaTarihi']
        }
        super(HizmetNufusEkle, self).handle()
