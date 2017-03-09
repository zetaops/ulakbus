# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Borclanma Ekle

Hitap'a personelin açık süre bilgilerinin eklenmesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetBorclanmaEkle(ZatoHitapService):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Borçlanma Bilgisi Ekleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetBorclanmaInsert',
        'fields': {
            'tckn': 'tckn',
            'ad': 'ad',
            'soyad': 'soyad',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'gunSayisi': 'gun_sayisi',
            'odenenMiktar': 'odenen_miktar',
            'toplamTutar': 'toplam_tutar',
            'kanunKod': 'kanun_kod',
            'borcNevi': 'borc_nevi',
            'borclanmaTarihi': 'borclanma_tarihi',
            'odemeTarihi': 'odeme_tarihi',
            'derece': 'derece',
            'kademe': 'kademe',
            'ekgosterge': 'ekgosterge',
            'emekliSicil': 'emekli_sicil',
            'calistigiKurum': 'calistigi_kurum',
            'isyeriIl': 'isyeri_il',
            'isyeriIlce': 'isyeri_ilce',
            'kurumOnayTarihi': 'kurum_onay_tarihi'
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'borclanma_tarihi', 'kurum_onay_tarihi'],
        'long_to_string': ['kayit_no'],
        'required_fields': ['tckn', 'ad', 'soyad', 'emekliSicil', 'derece', 'kademe',
                            'ekgosterge', 'baslamaTarihi', 'bitisTarihi', 'gunSayisi',
                            'kanunKod', 'borcNevi', 'toplamTutar', 'calistigiKurum', 'isyeriIl',
                            'isyeriIlce', 'kurumOnayTarihi']
    }
