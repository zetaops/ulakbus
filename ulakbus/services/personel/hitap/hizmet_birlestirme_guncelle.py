# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Hizmet Birlestirme Guncelle

Hitap'a personelin hizmet birlestirme bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetBirlestirmeGuncelle(ZatoHitapService):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Birlestirme Bilgisi Guncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetBirlestirmeUpdate',
        'service_mapper': 'ns1:HizmetBirlestirmeServisBean',
        'fields': {
            'kayitNo': 'kayit_no',
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
        'required_fields': ['tckn', 'kayitNo', 'sgkNevi', 'sgkSicilNo', 'baslamaTarihi',
                            'bitisTarihi', 'kurumOnayTarihi']
    }
