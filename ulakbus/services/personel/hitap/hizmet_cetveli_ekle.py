# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Cetvel Ekle

Hitap'a personelin Hizmet Cetvel  Kayit bilgilerinin eklenmesini yapar.

"""

__author__ = 'H.İbrahim Yılmaz (drlinux)'

from ulakbus.services.personel.hitap.hitap_ekle import HITAPEkle


class HizmetCetveliEkle(HITAPEkle):
    """
    HITAP Ekleme servisinden kalıtılmış Hizmet Okul Bilgi Ekleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): Request yoluyla gelen kayıtlar,
                    HizmetCetvelInsert servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """

        self.service_name = 'HizmetCetvelInsert'
        self.service_dict = {
            'fields': {
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
            'required_fields': ['tckn', 'gorev', 'unvanKod', 'hizmetSinifi', 'kadroDerece',
                                'odemeDerece', 'odemeKademe', 'odemeKademe', 'odemeEkGosterge',
                                'kazanilmisHakAyligiDerece', 'kazanilmisHakAyligiKademe',
                                'kazanilmisHakAyligiEkGosterge', 'emekliDerece', 'emekliKademe',
                                'emekliEkGosterge', 'sebepKod', 'kurumOnayTarihi']
        }
        super(HizmetCetveliEkle, self).handle()
