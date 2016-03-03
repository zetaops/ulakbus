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
from ulakbus.models.hitap import HizmetKayitlari


class HizmetCetveliGuncelle(HITAPGuncelle):
    """
    HITAP Guncelleme servisinden kalıtılmış Hizmet Okul Bilgi Güncelleme servisi

    """

    def handle(self):
        """Servis çağrıldığında tetiklenen metod.

        Attributes:
            service_name (str): İlgili Hitap sorgu servisinin adı
            service_dict (dict): ''HizmetKayitlari'' modelinden gelen kayıtların alanları,
                    HizmetCetvelUpdate servisinin alanlarıyla eşlenmektedir.
                    Filtreden geçecek tarih alanları listede tutulmaktadır.
        """
        key = self.request.payload['key']

        self.service_name = 'HizmetCetvelUpdate'
        hizmet_cetvel = HizmetKayitlari.objects.get(key)
        self.service_dict = {
            'fields': {
                'kayitNo': hizmet_cetvel.kayit_no,
                'baslamaTarihi': hizmet_cetvel.baslama_tarihi,
                'bitisTarihi': hizmet_cetvel.bitis_tarihi,
                'emekliDerece': hizmet_cetvel.emekli_derece,
                'emekliKademe': hizmet_cetvel.emekli_kademe,
                'gorev': hizmet_cetvel.gorev,
                'unvanKod': hizmet_cetvel.unvan_kod,
                'hizmetSinifi': hizmet_cetvel.hizmet_sinifi,
                'kazanilmisHakAyligiDerece': hizmet_cetvel.kazanilmis_hak_ayligi_derece,
                'kazanilmisHakAyligiKademe': hizmet_cetvel.kazanilmis_hak_ayligi_kademe,
                'odemeDerece': hizmet_cetvel.odeme_derece,
                'odemeKademe': hizmet_cetvel.odeme_kademe,
                'emekliEkGosterge': hizmet_cetvel.emekli_ekgosterge,
                'kadroDerece': hizmet_cetvel.kadro_derece,
                'kazanilmisHakAyligiEkGosterge': hizmet_cetvel.kazanilmis_hak_ayligi_ekgosterge,
                'odemeEkGosterge': hizmet_cetvel.odeme_ekgosterge,
                'sebepKod': hizmet_cetvel.sebep_kod,
                'tckn': hizmet_cetvel.tckn,
                'ucret': hizmet_cetvel.ucret,
                'yevmiye': hizmet_cetvel.yevmiye,
                'kurumOnayTarihi': hizmet_cetvel.kurum_onay_tarihi
            },
            'date_filter': ['baslamaTarihi', 'bitisTarihi', 'kurumOnayTarihi']
        }
        super(HizmetCetveliGuncelle, self).handle()
