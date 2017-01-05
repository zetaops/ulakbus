# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Mahkeme Ekle

Hitap'a personelin Mahkeme bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetMahkemeEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Mahkeme Bilgi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetMahkemeInsert',
        'fields': {
            'tckn': 'tckn',
            'mahkemeAd': 'mahkeme_ad',
            'sebep': 'sebep',
            'kararTarihi': 'karar_tarihi',
            'kararSayisi': 'karar_sayisi',
            'kesinlesmeTarihi': 'kesinlesme_tarihi',
            'asilDogumTarihi': 'asil_dogum_tarihi',
            'tashihDogumTarihi': 'tashih_dogum_tarihi',
            'gecerliDogumTarihi': 'gecerli_dogum_tarihi',
            'asilAd': 'asil_ad',
            'tashihAd': 'tashih_ad',
            'asilSoyad': 'asil_soyad',
            'tashihSoyad': 'tashih_soyad',
            'aciklama': 'aciklama',
            'gunSayisi': 'gun_sayisi',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['kesinlesmeTarihi', 'asilDogumTarihi', 'tashihDogumTarihi',
                        'gecerliDogumTarihi', 'kurumOnayTarihi'],
        'required_fields': ['tckn', 'mahkemeAd', 'sebep', 'kararTarihi', 'kararSayisi',
                            'kurumOnayTarihi']
    }
