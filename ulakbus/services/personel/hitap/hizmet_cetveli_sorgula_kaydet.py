# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
import os
from time import sleep
import urllib2
import socket

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Personel

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliSorgula(Service):
    """
    HITAP HizmetCetveliSorgula Zato Servisi
    """

    def handle(self):

        def pass_service_records(employee_passed_record, records):
            hizmet_kayitlari = employee_passed_record.HizmetKayitlari()

            # if service_list[i].baslamaTarihi == '01.01.0001': service_list[i].baslamaTarihi = '22.05.1942'
            # service_records.start_date = service_list[i].baslamaTarihi
            # if service_list[i].bitisTarihi == '01.01.0001': service_list[i].bitisTarihi = '22.05.1942'
            # service_records.end_date = service_list[i].bitisTarihi

            hizmet_kayitlari.emekli_derece = records['emekli_derece']
            hizmet_kayitlari.emekli_kademe = records['emekli_kademe']
            hizmet_kayitlari.gorev = records['gorev']
            hizmet_kayitlari.unvan_kod = records['unvan_kod']
            hizmet_kayitlari.hizmet_sinifi = records['hizmet_sinifi']
            hizmet_kayitlari.kayit_no = records['kayit_no']
            hizmet_kayitlari.kazanilmis_hak_ayligi_derece = records['kazanilmis_hak_ayligi_derece']
            hizmet_kayitlari.kazanilmis_hak_ayligi_kademe = records['kazanilmis_hak_ayligi_kademe']
            hizmet_kayitlari.odeme_derece = records['odeme_derece']
            hizmet_kayitlari.odeme_kademe = records['odeme_kademe']
            hizmet_kayitlari.emekli_ekgosterge = records['emekli_ek_gosterge']
            hizmet_kayitlari.kadro_derece = records['kadro_derece']
            hizmet_kayitlari.kazanilmis_hak_ayligi_ekgosterge = records['kazanilmis_hak_ayligi_ekgosterge']
            hizmet_kayitlari.odeme_ek_gosterge = records['odeme_ek_gosterge']
            hizmet_kayitlari.sebep_kod = records['sebep_kod']
            hizmet_kayitlari.tckn = records['tckn']
            try:
                hizmet_kayitlari.ucret = float(records['ucret'].strip())
            except ValueError:
                pass
            try:
                hizmet_kayitlari.yevmiye = float(records['yevmiye'].strip())
            except ValueError:
                pass
            hizmet_kayitlari.kurum_onay_tarihi = records['kurum_onay_tarihi']

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetCetvelSorgula(H_USER, H_PASS, tckn).HizmetCetveliServisBean
                self.logger.info("zato service started to work.")

                # collects data from HITAP {record_id: record_values_belong_to_that_record_id}
                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    hitap_dict[service_bean[record].kayitNo] = {
                        'baslama_tarihi': service_bean[record].baslamaTarihi,
                        'bitis_tarihi': service_bean[record].bitisTarihi,
                        'emekli_derece': service_bean[record].emekliDerece,
                        'emekli_kademe': service_bean[record].emekliKademe,
                        'gorev': service_bean[record].gorev,
                        'unvan_kod': service_bean[record].unvanKod,
                        'hizmet_sinifi': service_bean[record].hizmetSinifi,
                        'kayit_no': service_bean[record].kayitNo,
                        'kazanilmis_hak_ayligi_derece': service_bean[record].kazanilmisHakAyligiDerece,
                        'kazanilmis_hak_ayligi_kademe': service_bean[record].kazanilmisHakAyligiKademe,
                        'odeme_derece': service_bean[record].odemeDerece,
                        'odeme_kademe': service_bean[record].odemeKademe,
                        'emekli_ek_gosterge': service_bean[record].emekliEkGosterge,
                        'kadro_derece': service_bean[record].kadroDerece,
                        'kazanilmis_hak_ayligi_ekgosterge': service_bean[record].kazanilmisHakAyligiEkGosterge,
                        'odeme_ek_gosterge': service_bean[record].odemeEkGosterge,
                        'sebep_kod': service_bean[record].sebepKod,
                        'tckn': service_bean[record].tckn,
                        'ucret': service_bean[record].ucret,
                        'yevmiye': service_bean[record].yevmiye,
                        'kurum_onay_tarihi': service_bean[record].kurumOnayTarihi
                    }

                self.logger.info("hitap_dict created.")

                # if employee saved before, find that and add new records from hitap to riak
                try:
                    riak_dict_from_db_queries_with_pno = {}
                    employee = Personel.objects.filter(hizmet_kayitlari__tckn=tckn).get()
                    for record in employee.HizmetKayitlari:
                        riak_dict_from_db_queries_with_pno[record.kayit_no] = {
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
                            'kazanilmis_hak_ayligi_ekgosterge': record.kazanilmis_hak_ayligi_ekgosterge,
                            'odeme_ek_gosterge': record.odeme_ek_gosterge,
                            'sebep_kod': record.sebep_kod,
                            'tckn': record.tckn,
                            'ucret': record.ucret,
                            'yevmiye': record.yevmiye,
                            'kurum_onay_tarihi': record.kurum_onay_tarihi
                        }

                    self.logger.info("riak_dict_from_db_queries_with_pno created.")

                    for item in employee.HizmetKayitlari:
                        if not hitap_dict.has_key(item.kayit_no):
                            self.logger.info("item key: %s " % item.kayit_no)
                            item.remove()
                            self.logger.info("Service record deleted.")

                    for hitap_key, hitap_values in hitap_dict.items():
                        if not riak_dict_from_db_queries_with_pno.has_key(hitap_key):
                            pass_service_records(employee, hitap_values)

                    # if any record exists in riak but not in hitap delete it
                    employee.save()
                    self.logger.info("RIAK KEY: %s " % employee.key)
                    self.logger.info("employee saved. OLD RECORD")

                except IndexError:
                    employee = Personel()
                    employee.tckn = tckn
                    for record_id, record_values in hitap_dict.items():
                        pass_service_records(employee, record_values)
                        employee.save()
                        sleep(1)
                        self.logger.info("RIAK KEY: %s " % employee.key)
                        self.logger.info("employee saved. NEW RECORD (Index Error)")
                    sleep(1)
                except KeyError:
                    employee = Personel()
                    employee.tckn = tckn
                    for record_id, record_values in hitap_dict.items():
                        pass_service_records(employee, record_values)
                        employee.save()
                        sleep(1)
                        self.logger.info("RIAK KEY: %s " % employee.key)
                        self.logger.info("employee saved. NEW RECORD (Key Error)")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        # except AttributeError:
            # self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
