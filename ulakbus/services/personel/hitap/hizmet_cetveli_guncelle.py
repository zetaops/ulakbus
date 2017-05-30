# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Cetvel Guncelle

Hitap'a personelin Hizmet Cetvel Kayit bilgilerinin güncellemesini yapar.

"""

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService


class HizmetCetveliGuncelle(ZatoHitapService):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Okul Bilgi Güncelleme servisi

    """
    HAS_CHANNEL = True
    service_dict = {
        'service_name': 'HizmetCetvelUpdate',
        'fields': {
            'kayitNo': 'kayit_no',
            'baslamaTarihi': 'baslama_tarihi',
            'bitisTarihi': 'bitis_tarihi',
            'emekliDerece': 'emekli_derece',
            'emekliKademe': 'emekli_kademe',
            'gorev': 'gorev',
            'unvanKod': 'unvan_kod',
            'hizmetSinifi': 'hizmet_sinifi',
            'kazanilmisHakAyligiDerece': 
                'kazanilmis_hak_ayligi_derece',
            'kazanilmisHakAyligiKademe': 
                'kazanilmis_hak_ayligi_kademe',
            'odemeDerece': 'odeme_derece',
            'odemeKademe': 'odeme_kademe',
            'emekliEkGosterge': 'emekli_ekgosterge',
            'kadroDerece': 'kadro_derece',
            'kazanilmisHakAyligiEkGosterge': 
                'kazanilmis_hak_ayligi_ekgosterge',
            'odemeEkGosterge': 'odeme_ekgosterge',
            'sebepKod': 'sebep_kod',
            'tckn': 'tckn',
            'ucret': 'ucret',
            'yevmiye': 'yevmiye',
            'kurumOnayTarihi': 'kurum_onay_tarihi',
        },
        'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi'],
        'required_fields': ['kayitNo', 'emekliDerece', 'emekliKademe', 'gorev', 'unvanKod',
                            'hizmetSinifi', 'kazanilmisHakAyligiDerece',
                            'kazanilmisHakAyligiKademe', 'odemeDerece', 'odemeKademe',
                            'emekliEkGosterge', 'kadroDerece', 'kazanilmisHakAyligiEkGosterge',
                            'odemeEkGosterge', 'sebepKod', 'tckn', 'kurumOnayTarihi']
    }
