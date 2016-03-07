# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Cetvel Guncelle

Hitap'a personelin Hizmet Cetvel Kayit bilgilerinin güncellemesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_guncelle import HITAPGuncelle


class HizmetCetveliGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Okul Bilgi Güncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetCetvelUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetCetvelUpdate'
        self.service_dict = {
            'fields': {
                'kayitNo': self.request.payload['kayit_no'],
                'baslamaTarihi': self.request.payload['baslama_tarihi'],
                'bitisTarihi': self.request.payload['bitis_tarihi'],
                'emekliDerece': self.request.payload['emekli_derece'],
                'emekliKademe': self.request.payload['emekli_kademe'],
                'gorev': self.request.payload['gorev'],
                'unvanKod': self.request.payload['unvan_kod'],
                'hizmetSinifi': self.request.payload['hizmet_sinifi'],
                'kazanilmisHakAyligiDerece': self.request.payload['kazanilmis_hak_ayligi_derece'],
                'kazanilmisHakAyligiKademe': self.request.payload['kazanilmis_hak_ayligi_kademe'],
                'odemeDerece': self.request.payload['odeme_derece'],
                'odemeKademe': self.request.payload['odeme_kademe'],
                'emekliEkGosterge': self.request.payload['emekli_ekgosterge'],
                'kadroDerece': self.request.payload['kadro_derece'],
                'kazanilmisHakAyligiEkGosterge': self.request.payload[
                    'kazanilmis_hak_ayligi_ekgosterge'],
                'odemeEkGosterge': self.request.payload['odeme_ekgosterge'],
                'sebepKod': self.request.payload['sebep_kod'],
                'tckn': self.request.payload['tckn'],
                'ucret': self.request.payload['ucret'],
                'yevmiye': self.request.payload['yevmiye'],
                'kurumOnayTarihi': self.request.payload['kurum_onay_tarihi']
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi'],
            'required_fields': ['kayitNo', 'emekliDerece', 'emekliKademe', 'gorev', 'unvanKod',
                                'hizmetSinifi', 'kazanilmisHakAyligiDerece',
                                'kazanilmisHakAyligiKademe', 'odemeDerece', 'odemeKademe',
                                'emekliEkGosterge', 'kadroDerece', 'kazanilmisHakAyligiEkGosterge',
                                'odemeEkGosterge', 'sebepKod', 'tckn', 'kurumOnayTarihi']
        }
        super(HizmetCetveliGuncelle, self).handle()
