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
                'tckn': 'Tckn',
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
                'ucret':'ucret',
                'yevmiye': 'yevmiye',
                'kurum_onay_tarihi': 'kurumOnayTarihi'
            },
            'date_filter': ['baslama_tarihi', 'bitis_tarihi', 'kurum_onay_tarihi']
        }
        super(HizmetCetveliGetir, self).handle()

    def custom_filter(self, hitap_dict):
        for record in hitap_dict:
            record['hizmet_sinifi'] = self.hizmet_sinifi_int_kontrol(record['hizmet_sinifi'])

    def hizmet_sinifi_int_kontrol(self, hs):
        """
        Bu metot ilgili HITAP servisinin hizmet_sinifi alaninin, hem 1, 2, 3 ... 29 gibi integer degerler hem de
        GIH, MIAH, ... SOZ gibi string almasi problemini duzeltmek icindir.

        :param hs: hitaptan donen hizmet sinifi
        :type hs: str
        :return int: hitap sinifi int or 0

        """

        # TODO: key'lerin unicode olarak tutulmasi uygun mu
        hizmet_siniflari = {
            u"GİH": 1,
            u"MİAH": 2,
            u"SH": 3,
            u"TH": 4,
            u"EÖH": 5,
            u"AH": 6,
            u"EH": 7,
            u"DH": 8,
            u"YH": 9,
            u"MİT": 10,
            u"AHS": 11,
            u"BB": 12,
            u"CU": 13,
            u"CUM": 14,
            u"DE": 15,
            u"DVS": 16,
            u"HS": 17,
            u"MB": 18,
            u"MV": 19,
            u"ÖÜ": 20,
            u"SAY": 21,
            u"TBM": 22,
            u"TRT": 23,
            u"TSK": 24,
            u"YÖK": 25,
            u"YSH": 26,
            u"ÖGO": 27,
            u"ÖY": 28,
            u"SÖZ": 29
        }

        try:
            # eger int olabiliyorsa dogrudan dondur
            return int(hs)

        except ValueError:
            # int degilse  class 'suds.sax.text.Text' tipinde sozlukten karsiligini bul
            try:
                return hizmet_siniflari[hs.strip()]
            except KeyError:
                # TODO: admin'e bildirim gitmesi lazim
                self.logger.info("Hizmet Sinifini (%s) Kontrol Edin!", hs)
                return 0
