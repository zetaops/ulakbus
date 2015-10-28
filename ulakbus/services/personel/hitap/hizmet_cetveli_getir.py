# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
import os
from time import sleep
import urllib2
from json import dumps
import socket

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
                self.logger.info("zato service started to work.")

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
                        'hizmet_sinifi': service_bean[record].hizmetSinifi,
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
            self.response.payload = response_json

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
