# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
from zato.common import DATA_FORMAT
import os
from time import sleep
import urllib2
import socket
from json import loads, dumps
from datetime import datetime
from time import strftime
from suds.client import Client

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.hitap import HizmetKayitlari

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliUpdate(Service):
    """
    HITAP HizmetCetveliUpdate Zato Servisi
    """

    def handle(self):
        # Save a dictionary into a pickle file.


        self.logger.info("zato service started to work.")

        tckn = self.request.payload['tckn']
        update_credentials = self.request.payload['update_credentials']

        conn = self.outgoing.soap['HITAP'].conn

        self.logger.info("Payload tckn: %s" % tckn)
        self.logger.info("Update credentials: %s" % update_credentials)

        # to make a backup on development process
        # import pickle
        # dict_to_save = update_credentials
        #
        # pickle.dump(dict_to_save, open("hitap_update_backup.p", "wb"))
        #
        # rescued_dict = pickle.load(open("hitap_update_backup.p", "rb"))
        #
        # self.logger.info("RESCUED DATA: %s" % rescued_dict)

        service_record = HizmetKayitlari.objects.filter(kayit_no=999999999999999).get()

        '''
        Tckn = TCKN,
        kayitNo = KAYIT_NO,
        baslamaTarihi = BASLAMA_TARIHI,
        bitisTarihi = BITIS_TARIHI,
        gorev = GOREV,
        unvanKod = UNVAN_KOD,
        yevmiye = YEVMIYE,
        ucret = UCRET,
        hizmetSinifi = HIZMET_SINIFI,
        kadroDerece = KADRO_DERECE,
        odemeDerece = ODEME_DERECE,
        odemeKademe = ODEME_KADEME,
        odemeEkGosterge = ODEME_EK_GOSTERGE,
        kazanilmisHakAyligiDerece = KAZANILMIS_HAK_AYLIGI_DERECE,
        kazanilmisHakAyligiKademe = KAZANILMIS_HAK_AYLIGI_KADEME,
        kazanilmisHakAyligiEkGosterge = KAZANILMIS_HAK_AYLIGI_EK_GOSTERGE,
        hizmetSinifi = HIZMET_SINIFI,
        emekliDerece = EMEKLI_DERECE,
        emekliKademe = EMEKLI_KADEME,
        emekliEkGosterge = EMEKLI_EK_GOSTERGE,
        sebepKod = SEBEP_KOD,
        kurumOnayTarihi = KURUM_ONAY_TARIHI,
        kullaniciAd = KULLANICI_AD,
        sifre = SIFRE
        '''

        TCKN = int(service_record.tckn)
        KAYIT_NO = int(service_record.kayit_no)
        BASLAMA_TARIHI = service_record.baslama_tarihi.strftime('%m/%d/%Y')
        BITIS_TARIHI = service_record.bitis_tarihi.strftime('%m/%d/%Y')
        GOREV = service_record.gorev
        UNVAN_KOD = int(service_record.unvan_kod)
        YEVMIYE = service_record.yevmiye
        UCRET = service_record.ucret
        HIZMET_SINIFI = service_record.hizmet_sinifi
        KADRO_DERECE = service_record.kadro_derece
        ODEME_DERECE = int(service_record.odeme_derece)
        ODEME_KADEME = int(service_record.odeme_kademe)
        ODEME_EK_GOSTERGE = int(service_record.odeme_ekgosterge)
        KAZANILMIS_HAK_AYLIGI_DERECE = int(service_record.kazanilmis_hak_ayligi_derece)
        KAZANILMIS_HAK_AYLIGI_KADEME = int(service_record.kazanilmis_hak_ayligi_kademe)
        KAZANILMIS_HAK_AYLIGI_EK_GOSTERGE = int(service_record.kazanilmis_hak_ayligi_ekgosterge)
        EMEKLI_DERECE = int(service_record.emekli_derece)
        EMEKLI_KADEME = int(service_record.emekli_kademe)
        EMEKLI_EK_GOSTERGE = int(service_record.emekli_ekgosterge)
        SEBEP_KOD = int(service_record.sebep_kod)
        KURUM_ONAY_TARIHI = ""
        KULLANICI_AD = str(H_USER)
        SIFRE = str(H_PASS)

        WSDL_URL = "https://hitap.sgk.gov.tr/WS_HizmetTakip/services/Hitap4cWEBBean/wsdl/Hitap4cWEBBean.wsdl"

        HITAP_TEST_TCKN = 999999999999
        HITAP_USER = 999999999999
        HITAP_PASS = 999999999999

        # client = Client(WSDL_URL, retxml=False)
        # result = client.service.HizmetCetvelSorgula(kullaniciAd=HITAP_USER,sifre=HITAP_PASS,tckn=HITAP_TEST_TCKN)

        hizmet_cetveli = {'tckn': TCKN,
                          'kayitNo': KAYIT_NO,
                          'baslamaTarihi': BASLAMA_TARIHI,
                          'bitisTarihi': BITIS_TARIHI,
                          'gorev': GOREV,
                          'unvanKod': UNVAN_KOD,
                          'yevmiye': YEVMIYE,
                          'ucret': UCRET,
                          'hizmetSinifi': HIZMET_SINIFI,
                          'kadroDerece': KADRO_DERECE,
                          'odemeDerece': ODEME_DERECE,
                          'odemeKademe': ODEME_KADEME,
                          'odemeEkGosterge': ODEME_EK_GOSTERGE,
                          'kazanilmisHakAyligiDerece': KAZANILMIS_HAK_AYLIGI_DERECE,
                          'kazanilmisHakAyligiKademe': KAZANILMIS_HAK_AYLIGI_KADEME,
                          'kazanilmisHakAyligiEkGosterge': KAZANILMIS_HAK_AYLIGI_EK_GOSTERGE,
                          'emekliDerece': EMEKLI_DERECE,
                          'emekliKademe': EMEKLI_KADEME,
                          'emekliEkGosterge': EMEKLI_EK_GOSTERGE,
                          'sebepKod': SEBEP_KOD,
                          'kurumOnayTarihi': KURUM_ONAY_TARIHI}
        self.logger.info("Client: %s" % conn.client)

        client = Client(WSDL_URL, retxml=False)  # , faults=False)

        result = client.service.HizmetCetvelUpdate(hizmetCetveli=hizmet_cetveli,
                                                   kullaniciAd=KULLANICI_AD,
                                                   sifre=SIFRE)
        self.logger.info("RESULT: %s" % (result,))

        # result = client.service.HizmetCetvelUpdate(hizmetCetveli=hizmet_cetveli, kullaniciAd=KULLANICI_AD, sifre=SIFRE)

        # with conn.client() as client:
        #     result = client.service.HizmetCetvelUpdate(hizmetCetveli=hizmet_cetveli,
        #                                                kullaniciAd=KULLANICI_AD,
        #                                                sifre=SIFRE)
        #
        # self.logger.info("RESULT: %s" % result)

        '''
        for k, v in hitap_dict.items():
            if k not in local_records:
                print "Bu kayit localde yok! => " + str(k)

        for k, v in local_records.items():
            if k not in hitap_dict:
                print "Bu kayit hitapta yok! => " + str(k)
        '''

        self.logger.info("zato service finished.")
