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
            self.logger.info(local_records)
            self.logger.info("local_records created.")
            for kayit in HizmetKayitlari.objects.filter(tckn=tckn):
                self.logger.info("Localdeki kayit no: " + str(kayit.kayit_no))
            for record_id in hitap_dict.keys():
                self.logger.info("Hitap dictteki kayit no: " + str(record_id))
            # compare hitap incoming data and local db

            self.logger.info("Localdeki kayit sayisi: " + str(len(local_records)))
            self.logger.info("Hitaptan gelen kayit sayisi: " + str(len(hitap_dict)))

            for record_id, record_values in hitap_dict.items():
                if record_id in local_records:
                    self.logger.info("hitap gelen data localde var.")
                    hizmet_kayitlari = HizmetKayitlari.objects.filter(kayit_no=record_id).get()
                    if hizmet_kayitlari.sync == 1:
                        self.logger.info("hitaptan gelen data localde var ve senkronize.")
                        pass
                    elif hizmet_kayitlari.sync == 2:
                        self.logger.info("hitap gelen data localde senkronize edildi.")
                        pass_hizmet_kayitlari(hizmet_kayitlari, record_values)
                        hizmet_kayitlari.sync = 1
                        hizmet_kayitlari.save()
                    else:
                        pass
                else:
                    for k in local_records.keys():
                        self.logger.info("Localdeki keyler: " + str(k))
                    self.logger.info("Hitaptan gelen localde olmayan key: " + str(record_id))

                    hizmet_kayitlari = HizmetKayitlari()
                    pass_hizmet_kayitlari(hizmet_kayitlari, record_values)
                    hizmet_kayitlari.sync = 1
                    hizmet_kayitlari.save()
                    self.logger.info("hitap gelen data localde yok. yenisi kaydedildi.")

            # compare local db and hitap incoming data
            for record_id, record_values in local_records.items():
                if record_id not in hitap_dict:
                    hizmet_kayitlari = HizmetKayitlari.objects.filter(kayit_no=record_id).get()
                    if hizmet_kayitlari.sync == 1:
                        hizmet_kayitlari.delete()
                    else:
                        pass

                # hizmet_kayitlari.save()
            self.logger.info("Service runned.")

        # If not any record belongs to given tcno, create new one
        # except IndexError:
        #     for hitap_keys, hitap_values in hitap_dict.items():
        #         hizmet_kayitlari = HizmetKayitlari()
        #         pass_hizmet_kayitlari(hizmet_kayitlari, hitap_values)
        #         hizmet_kayitlari.sync = 1
        #         hizmet_kayitlari.save()
        #         self.logger.info("New HizmetKayitlari saved.")
        #     sleep(1)
        except socket.error:
            self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
