# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Nufus Guncelle

Hitap'a personelin Nufus bilgilerinin guncellenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetNufusGuncelle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Nufus Bilgi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetNufusUpdate',
        'fields': {
            'ad': 'ad',
            'cinsiyet': 'cinsiyet',
            'dogumTarihi': 'dogum_tarihi',
            'durum': 'durum',
            'emekliSicilNo': 'emekli_sicil_no',
            'ilkSoyad': 'ilk_soy_ad',
            'kurumSicili': 'kurum_sicil',
            'maluliyetKod': 'maluliyet_kod',
            'memuriyetBaslamaTarihi': 'memuriyet_baslama_tarihi',
            'sebep': 'sebep',
            'soyad': 'soyad',
            'tckn': 'tckn',
            'aciklama': 'aciklama',
            'yetkiSeviyesi': 'yetki_seviyesi',
            'kurumaBaslamaTarihi': 'kuruma_baslama_tarihi',
            'gorevTarihi6495': 'gorev_tarihi_6495',
            'emekliSicil6495': 'emekli_sicil_6495'
        },
        'date_filter': ['dogum_tarihi', 'memuriyet_baslama_tarihi', 'kuruma_baslama_tarihi'],
        'required_fields': ['tckn', 'ad', 'soyad', 'dogumTarihi', 'cinsiyet', 'emekliSicilNo',
                            'memuriyetBaslamaTarihi', 'durum', 'kurumSicili', 'maluliyetKod',
                            'sebep', 'yetkiSeviyesi']

    }
