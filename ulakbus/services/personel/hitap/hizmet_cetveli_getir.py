# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.personel.hitap.hitap_service import HITAPService


class HizmetCetveliGetir(HITAPService):
    """
    HITAP HizmetCetveliGetir Zato Servisi
    """

    def handle(self):
        self.service_name = 'HizmetCetvelSorgula'
        self.bean_name = 'HizmetCetveliServisBean'
        self.service_dict = {
            'fields': {
                'baslama_tarihi': 'baslamaTarihi',
                'bitis_tarihi': 'bitisTarihi',
                'emekli_derece': 'emekliDerece',
                'emekli_kademe': 'emekliKademe',
                'gorev': 'gorev',
                'unvan_kod': 'unvanKod',
                'hizmet_sinifi': 'hizmetSinifi',
                'kayit_no': 'kayitNo',
                'kazanilmis_hak_ayligi_derece': 'kazanilmisHakAyligiDerece',
                'kazanilmis_hak_ayligi_kademe': 'kazanilmisHakAyligiKademe',
                'odeme_derece': 'odemeDerece',
                'odeme_kademe': 'odemeKademe',
                'emekli_ek_gosterge': 'emekliEkGosterge',
                'kadro_derece': 'kadroDerece',
                'kazanilmis_hak_ayligi_ekgosterge': 'kazanilmisHakAyligiEkGosterge',
                'odeme_ekgosterge': 'odemeEkGosterge',
                'sebep_kod': 'sebepKod',
                'tkcn': 'tckn',
                'ucret':'ucret',
                'yevmiye': 'yevmiye',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetCetveliGetir, self).handle()

    def custom_filter(self, hitap_dict):
        hitap_dict['hizmet_sinifi'] = self.hizmet_sinifi_int_kontrol(hitap_dict['hizmet_sinifi'])

    def hizmet_sinifi_int_kontrol(self, hs):
        """
        Bu metod ilgili HITAP servisinin hizmet_sinifi alaninin, hem 1, 2, 3 ... 29 gibi integer degerler hem de
        GIH, MIAH, ... SOZ gibi string almasi problemini duzeltmek icindir.

        :param hs: hitaptan donen hizmet sinifi
        :type hs: str
        :return int: hitap sinifi int or 0

        """
        hizmet_siniflari = {
            "GİH": 1,
            "MİAH": 2,
            "SH": 3,
            "TH": 4,
            "EÖH": 5,
            "AH": 6,
            "EH": 7,
            "DH": 8,
            "YH": 9,
            "MİT": 10,
            "AHS": 11,
            "BB": 12,
            "CU": 13,
            "CUM": 14,
            "DE": 15,
            "DVS": 16,
            "HS": 17,
            "MB": 18,
            "MV": 19,
            "ÖÜ": 20,
            "SAY": 21,
            "TBM": 22,
            "TRT": 23,
            "TSK": 24,
            "YÖK": 25,
            "YSH": 26,
            "ÖGO": 27,
            "ÖY": 28,
            "SÖZ": 29
        }

        if type(hs) is str:
            return hizmet_siniflari[hs.strip()]
        elif type(hs) is int and hs in range(1, 30):
            return hs
        else:
            self.logger.info("HIZMET SINIFINI KONTROL EDIN")
            return 0
