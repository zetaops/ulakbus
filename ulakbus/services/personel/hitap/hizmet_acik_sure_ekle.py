# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle

"""HITAP Açık Süre Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""


class HizmetAcikSureEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Açık Süre Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True

    service_dict = {
        'service_name': 'HizmetAcikSureInsert',
        'fields': {
            'tckn': 'tckn',
            'acikSekil': 'acik_sekil',
            'iadeSekil': 'iade_sekil',
            'hizmetDurum': 'hizmet_durum',
            'husus': 'husus',
            'acigaAlinmaTarih': 'aciga_alinma_tarih',
            'goreveSonTarih': 'goreve_son_tarih',
            'goreveIadeIstemTarih': 'goreve_iade_istem_tarih',
            'goreveIadeTarih': 'goreve_iade_tarih',
            'acikAylikBasTarihi': 'acik_aylik_bas_tarih',
            'acikAylikBitTarihi': 'acik_aylik_bit_tarih',
            'gorevSonAylikBasTarihi': 'goreve_son_aylik_bas_tarih',

            'gorevSonAylikBitTarihi': 'goreve_son_aylik_bit_tarih',

            'SYonetimKaldTarih': 's_yonetim_kald_tarih',
            'aciktanAtanmaTarih': 'aciktan_atanma_tarih',
            'kurumOnayTarihi': 'kurum_onay_tarihi',
        },
        'date_filter': ['acigaAlinmaTarih', 'goreveSonTarih', 'goreveIadeIstemTarih',
                        'goreveIadeTarih', 'acikAylikBasTarihi', 'acikAylikBitTarihi',
                        'gorevSonAylikBasTarihi', 'gorevSonAylikBitTarihi', 'SYonetimKaldTarih',
                        'aciktanAtanmaTarih', 'kurumOnayTarihi'],
        'required_fields': ['tckn', 'acikSekil', 'durum', 'hizmetDurum', 'husus',
                            'kurumOnayTarihi']
    }
