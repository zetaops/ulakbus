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

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.hitap import HizmetKayitlari

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliSenkronizeEt(Service):
    """
    HITAP HizmetCetveliSenkronizeEt Zato Servisi
    """

    def handle(self):

        def pass_hizmet_kayitlari(hizmet_kayitlari_passed, values):
            hizmet_kayitlari_passed.baslama_tarihi = values['baslama_tarihi']
            hizmet_kayitlari_passed.bitis_tarihi = values['bitis_tarihi']
            hizmet_kayitlari_passed.emekli_derece = values['emekli_derece']
            hizmet_kayitlari_passed.emekli_kademe = values['emekli_kademe']
            hizmet_kayitlari_passed.gorev = values['gorev']
            hizmet_kayitlari_passed.unvan_kod = values['unvan_kod']
            hizmet_kayitlari_passed.hizmet_sinifi = values['hizmet_sinifi']
            hizmet_kayitlari_passed.kayit_no = values['kayit_no']
            hizmet_kayitlari_passed.kazanilmis_hak_ayligi_derece = values[
                'kazanilmis_hak_ayligi_derece']
            hizmet_kayitlari_passed.kazanilmis_hak_ayligi_kademe = values[
                'kazanilmis_hak_ayligi_kademe']
            hizmet_kayitlari_passed.odeme_derece = values['odeme_derece']
            hizmet_kayitlari_passed.odeme_kademe = values['odeme_kademe']
            hizmet_kayitlari_passed.emekli_ekgosterge = values['emekli_ek_gosterge']
            hizmet_kayitlari_passed.kadro_derece = values['kadro_derece']
            hizmet_kayitlari_passed.kazanilmis_hak_ayligi_ekgosterge = values[
                'kazanilmis_hak_ayligi_ekgosterge']
            hizmet_kayitlari_passed.odeme_ekgosterge = values['odeme_ekgosterge']
            hizmet_kayitlari_passed.sebep_kod = values['sebep_kod']
            hizmet_kayitlari_passed.tckn = values['tckn']
            try:
                hizmet_kayitlari_passed.ucret = float(values['ucret'].strip())
            except ValueError:
                pass
            try:
                hizmet_kayitlari_passed.yevmiye = float(values['yevmiye'].strip())
            except ValueError:
                pass
            hizmet_kayitlari_passed.kurum_onay_tarihi = values['kurum_onay_tarihi']

            self.logger.info("hizmet_kayitlari successfully passed.")

        self.logger.info("zato service started to work.")

        tckn = self.request.payload['tckn']

        input_data = {'tckn': tckn}
        input_data = dumps(input_data)
        service_name = 'hizmet-cetveli-getir.hizmet-cetveli-getir'
        response = self.invoke(service_name, input_data, data_format=DATA_FORMAT.JSON, as_bunch=True)

        response_status = response["status"]
        if response_status == 'ok':
            hitap_dict = loads(response["result"])
            self.logger.info("hitap_dict created.")
        else:
            hitap_dict = {}
            self.logger.info("hitap_dict cannot created.")

        # if employee saved before, find that and add new records from hitap to riak
        try:
            local_records = {}
            # hizmet_kayitlari_list = HizmetKayitlari.objects.filter(tckn=tckn)
            for record in HizmetKayitlari.objects.filter(tckn=tckn):
                local_records[record.kayit_no] = {
                    'baslama_tarihi': record.baslama_tarihi,
                    'bitis_tarihi': record.bitis_tarihi,
                    'emekli_derece': record.emekli_derece,
                    'emekli_kademe': record.emekli_kademe,
                    'gorev': record.gorev,
                    'unvan_kod': record.unvan_kod,
                    'hizmet_sinifi': record.hizmet_sinifi,
                    'kayit_no': record.kayit_no,
                    'kazanilmis_hak_ayligi_derece': record.kazanilmis_hak_ayligi_derece,
                    'kazanilmis_hak_ayligi_kademe': record.kazanilmis_hak_ayligi_kademe,
                    'odeme_derece': record.odeme_derece,
                    'odeme_kademe': record.odeme_kademe,
                    'emekli_ekgosterge': record.emekli_ekgosterge,
                    'kadro_derece': record.kadro_derece,
                    'kazanilmis_hak_ayligi_ekgosterge':
                        record.kazanilmis_hak_ayligi_ekgosterge,
                    'odeme_ekgosterge': record.odeme_ekgosterge,
                    'sebep_kod': record.sebep_kod,
                    'tckn': record.tckn,
                    'ucret': record.ucret,
                    'yevmiye': record.yevmiye,
                    'kurum_onay_tarihi': record.kurum_onay_tarihi
                }

            # for k, v in local_records.iteritems():
            #     self.logger.info("Localdeki keyler => %s type %s" % (str(k), type(k)))

            # self.logger.info(local_records)
            self.logger.info("local_records created.")

            self.logger.info("Localdeki kayit sayisi: " + str(len(local_records)))
            self.logger.info("Hitaptan gelen kayit sayisi: " + str(len(hitap_dict)))

            '''
            for k, v in hitap_dict.items():
                if k not in local_records:
                    print "Bu kayit localde yok! => " + str(k)

            for k, v in local_records.items():
                if k not in hitap_dict:
                    print "Bu kayit hitapta yok! => " + str(k)
            '''

            # compare hitap incoming data and local db
            for hitap_key, hitap_values in hitap_dict.items():
                # self.logger.info("Hitap key: %s type %s" % (hitap_key, type(hitap_key)))
                if int(hitap_key) in local_records:
                    self.logger.info("hitap gelen data localde var.")
                    hizmet_kayitlari = HizmetKayitlari.objects.filter(kayit_no=hitap_key).get()
                    if hizmet_kayitlari.sync == 1:
                        self.logger.info("hitaptan gelen data localde var ve senkronize.")
                    elif hizmet_kayitlari.sync == 2:
                        self.logger.info("hitap gelen data localde senkronize edildi.")
                        pass_hizmet_kayitlari(hizmet_kayitlari, hitap_values)
                        hizmet_kayitlari.sync = 1
                        hizmet_kayitlari.save()
                        # sleep(1.5)
                    else:
                        pass
                else:
                    self.logger.info("hitap gelen data localde yok. Kayit no => " + str(hitap_key))
                    hizmet_kayitlari = HizmetKayitlari()
                    pass_hizmet_kayitlari(hizmet_kayitlari, hitap_values)
                    hizmet_kayitlari.sync = 1
                    hizmet_kayitlari.save()
                    # sleep(1.5)

            # compare local db and hitap incoming data
            for record_id, record_values in local_records.items():
                if unicode(record_id) not in hitap_dict:
                    hizmet_kayitlari = HizmetKayitlari.objects.filter(kayit_no=record_id).get()
                    if hizmet_kayitlari.sync == 1:
                        hizmet_kayitlari.delete()
                        self.logger.info("localdeki sync data, hitapta yok, kayit no degismis olabilir, kayit silindi.")
                    else:
                        pass
                else:
                    if hizmet_kayitlari.sync != 1 or hizmet_kayitlari.sync != 2:
                        hizmet_kayitlari.delete()

                # hizmet_kayitlari.save()
            self.logger.info("Service runned.")

        # If not any record belongs to given tcno, create new one
        except IndexError:
            for hitap_keys, hitap_values in hitap_dict.items():
                hizmet_kayitlari = HizmetKayitlari()
                pass_hizmet_kayitlari(hizmet_kayitlari, hitap_values)
                hizmet_kayitlari.sync = 1
                hizmet_kayitlari.save()
                self.logger.info("New HizmetKayitlari saved.")
            # sleep(1)
        except socket.error:
            self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
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
