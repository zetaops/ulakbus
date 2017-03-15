# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Birleştirme Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetBirlestirmeEkle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Birlestirme Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetBirlestirmeInsert',
        'service_mapper': 'ns1:HizmetBirlestirmeServisBean',
        'fields': {
            'tckn': 'tckn',
            'sgkNevi': 'sgk_nevi',
            'sgkSicilNo': 'sgk_sicil_no',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'kamuIsyeriAd': 'kamu_isyeri_ad',
            'ozelIsyeriAd': 'ozel_isyeri_ad',
            'bagKurMeslek': 'bag_kur_meslek',
            'ulkeKod': 'ulke_kod',
            'bankaSandikKod': 'banka_sandik_kod',
            'kidemTazminatOdemeDurumu': 'kidem_tazminat_odeme_durumu',

            'ayrilmaNedeni': 'ayrilma_nedeni',
            'sure': 'sure',
            'khaDurum': 'kha_durum',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi'],
        'long_to_string': ['kayit_no'],
        'required_fields': ['tckn', 'sgkNevi', 'sgkSicilNo', 'baslamaTarihi',
                            'bitisTarihi', 'sure', 'kurumOnayTarihi']
    }
