# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_sorgula import HITAPSorgula


class HizmetNufusGetir(HITAPSorgula):
    """
    HITAP HizmetNufusGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetNufusSorgula'
        self.bean_name = 'HizmetNufusServisBean'
        self.service_dict = {
            'fields': {
                'tckn': 'tckn',
                'ad': 'ad',
                'soyad': 'soyad',
                'ilk_soy_ad': 'ilkSoyAd',
                'dogum_tarihi': 'dogumTarihi',
                'cinsiyet': 'cinsiyet',
                'emekli_sicil_no': 'emekliSicilNo',
                'memuriyet_baslama_tarihi': 'memuriyetBaslamaTarihi',
                'kurum_sicil': 'kurumSicili',
                'maluliyet_kod': 'maluliyetKod',
                'yetki_seviyesi': 'yetkiSeviyesi',
                'aciklama': 'aciklama',
                'kuruma_baslama_tarihi': 'kurumaBaslamaTarihi',
                'gorev_tarihi_6495': 'gorevTarihi6495',
                'emekli_sicil_6495': 'emekliSicil6495',
                'durum': 'durum',
                'sebep': 'sebep'
            },
            'date_filter': ['dogum_tarihi', 'memuriyet_baslama_tarihi', 'kuruma_baslama_tarihi']
        }
        super(HizmetNufusGetir, self).handle()

