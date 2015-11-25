# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
import os
import urllib2
from json import dumps

# os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
# from ulakbus.models.hitap import HizmetKayitlari

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliGetir(Service):
    """
    HITAP HizmetCetveliGetir Zato Servisi
    """

    def handle(self):
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetCetvelSorgula(H_USER, H_PASS,
                                                                  tckn).HizmetCetveliServisBean
                self.logger.info("HizmetCetveliGetir started to work.")

                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    hitap_dict[service_bean[record].kayitNo] = {
                        'baslama_tarihi': '01.01.1900' if
                        service_bean[record].baslamaTarihi == "01.01.0001" else
                        service_bean[record].baslamaTarihi,
                        'bitis_tarihi': '01.01.1900' if
                        service_bean[record].bitisTarihi == "01.01.0001" else
                        service_bean[record].bitisTarihi,
                        'emekli_derece': service_bean[record].emekliDerece,
                        'emekli_kademe': service_bean[record].emekliKademe,
                        'gorev': service_bean[record].gorev,
                        'unvan_kod': service_bean[record].unvanKod,
                        'hizmet_sinifi': self.hizmet_sinifi_int_kontrol(service_bean[record].hizmetSinifi),
                        'kayit_no': service_bean[record].kayitNo,
                        'kazanilmis_hak_ayligi_derece': service_bean[
                            record].kazanilmisHakAyligiDerece,
                        'kazanilmis_hak_ayligi_kademe': service_bean[
                            record].kazanilmisHakAyligiKademe,
                        'odeme_derece': service_bean[record].odemeDerece,
                        'odeme_kademe': service_bean[record].odemeKademe,
                        'emekli_ek_gosterge': service_bean[record].emekliEkGosterge,
                        'kadro_derece': service_bean[record].kadroDerece,
                        'kazanilmis_hak_ayligi_ekgosterge': service_bean[
                            record].kazanilmisHakAyligiEkGosterge,
                        'odeme_ekgosterge': service_bean[record].odemeEkGosterge,
                        'sebep_kod': service_bean[record].sebepKod,
                        'tckn': service_bean[record].tckn,
                        'ucret': service_bean[record].ucret,
                        'yevmiye': service_bean[record].yevmiye,
                        'kurum_onay_tarihi': '01.01.1900' if
                        service_bean[record].kurumOnayTarihi == "01.01.0001" else service_bean[
                            record].kurumOnayTarihi
                    }
                self.logger.info("hitap_dict created.")

            response_json = dumps(hitap_dict)
            return_dict = {"status": "ok", "result": response_json}
            # self.response.payload = dumps(return_dict)
            self.response.payload = {"status": "ok", "result": response_json}
            # self.response.payload["status"] = "ok"
            # self.response.payload["result"] = response_json

        except AttributeError:
            self.response.payload["status"] = "error"
            self.response.payload["result"] = "TCKN may be wrong!"
            self.logger.info("TCKN may be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")

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
