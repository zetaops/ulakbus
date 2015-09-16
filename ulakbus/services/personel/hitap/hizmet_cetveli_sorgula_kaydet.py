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

        def pass_service_records(personel, record_values):
            # if service_list[i].baslamaTarihi == '01.01.0001': service_list[i].baslamaTarihi = '22.05.1942'
            # service_records.start_date = service_list[i].baslamaTarihi
            # if service_list[i].bitisTarihi == '01.01.0001': service_list[i].bitisTarihi = '22.05.1942'
            # service_records.end_date = service_list[i].bitisTarihi
            hizmet_kayitlari = personel.HizmetKayitlari()
            hizmet_kayitlari.retirement_degree = record_values['emekliDerece']
            hizmet_kayitlari.retirement_grade = record_values['emekliKademe']
            hizmet_kayitlari.assignment = record_values['gorev']
            hizmet_kayitlari.title_code = record_values['unvanKod']
            hizmet_kayitlari.duty_class = record_values['hizmetSinifi']
            hizmet_kayitlari.record_id = record_values['kayitNo']
            hizmet_kayitlari.aquired_degree = record_values['kazanilmisHakAyligiDerece']
            hizmet_kayitlari.aquired_grade = record_values['kazanilmisHakAyligiKademe']
            hizmet_kayitlari.salary_degree = record_values['odemeDerece']
            hizmet_kayitlari.salary_grade = record_values['odemeKademe']
            hizmet_kayitlari.retirement_indicator = record_values['emekliEkGosterge']
            hizmet_kayitlari.position_degree = record_values['kadroDerece']
            hizmet_kayitlari.aquired_sup_indicator = record_values['kazanilmisHakAyligiEkGosterge']
            hizmet_kayitlari.salary_sup_indicator = record_values['odemeEkGosterge']
            hizmet_kayitlari.reason_code = record_values['sebepKod']
            hizmet_kayitlari.pno = record_values['tckn']
            try:
                hizmet_kayitlari.salary = float(record_values['ucret'].strip())
            except ValueError:
                pass
            try:
                hizmet_kayitlari.wage = float(record_values['yevmiye'].strip())
            except ValueError:
                pass
            hizmet_kayitlari.approval_date = record_values['kurumOnayTarihi']

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
                        'baslamaTarihi': service_bean[record].baslamaTarihi,
                        'bitisTarihi': service_bean[record].bitisTarihi,
                        'emekliDerece': service_bean[record].emekliDerece,
                        'emekliKademe': service_bean[record].emekliKademe,
                        'gorev': service_bean[record].gorev,
                        'unvanKod': service_bean[record].unvanKod,
                        'hizmetSinifi': service_bean[record].hizmetSinifi,
                        'kayitNo': service_bean[record].kayitNo,
                        'kazanilmisHakAyligiDerece': service_bean[record].kazanilmisHakAyligiDerece,
                        'kazanilmisHakAyligiKademe': service_bean[record].kazanilmisHakAyligiKademe,
                        'odemeDerece': service_bean[record].odemeDerece,
                        'odemeKademe': service_bean[record].odemeKademe,
                        'emekliEkGosterge': service_bean[record].emekliEkGosterge,
                        'kadroDerece': service_bean[record].kadroDerece,
                        'kazanilmisHakAyligiEkGosterge': service_bean[record].kazanilmisHakAyligiEkGosterge,
                        'odemeEkGosterge': service_bean[record].odemeEkGosterge,
                        'sebepKod': service_bean[record].sebepKod,
                        'tckn': service_bean[record].tckn,
                        'ucret': service_bean[record].ucret,
                        'yevmiye': service_bean[record].yevmiye,
                        'kurumOnayTarihi': service_bean[record].kurumOnayTarihi
                    }

                self.logger.info("hitap_dict created.")

                # if employee saved before, find that and add new records from hitap to riak
                try:
                    riak_dict_from_db_queries_with_pno = {}
                    personel = Personel.objects.filter(pno=tckn).get()
                    for record in personel.HizmetKayitlari:
                        riak_dict_from_db_queries_with_pno[record.record_id] = {
                            'baslamaTarihi': record.baslamaTarihi,
                            'bitisTarihi': record.bitisTarihi,
                            'emekliDerece': record.emekliDerece,
                            'emekliKademe': record.emekliKademe,
                            'gorev': record.gorev,
                            'unvanKod': record.unvanKod,
                            'hizmetSinifi': record.hizmetSinifi,
                            'kayitNo': record.kayitNo,
                            'kazanilmisHakAyligiDerece': record.kazanilmisHakAyligiDerece,
                            'kazanilmisHakAyligiKademe': record.kazanilmisHakAyligiKademe,
                            'odemeDerece': record.odemeDerece,
                            'odemeKademe': record.odemeKademe,
                            'emekliEkGosterge': record.emekliEkGosterge,
                            'kadroDerece': record.kadroDerece,
                            'kazanilmisHakAyligiEkGosterge': record.kazanilmisHakAyligiEkGosterge,
                            'odemeEkGosterge': record.odemeEkGosterge,
                            'sebepKod': record.sebepKod,
                            'tckn': record.tckn,
                            'ucret': record.ucret,
                            'yevmiye': record.yevmiye,
                            'kurumOnayTarihi': record.kurumOnayTarihi
                        }

                    self.logger.info("riak_dict_from_db_queries_with_pno created.")

                    for item in personel.HizmetKayitlari:
                        if not hitap_dict.has_key(item.record_id):
                            self.logger.info("item key: %s " % (item.record_id))
                            item.remove()
                            self.logger.info("Service record deleted.")

                    for hitap_key, hitap_values in hitap_dict.items():
                        if not riak_dict_from_db_queries_with_pno.has_key(hitap_key):
                            pass_service_records(personel, hitap_values)

                    # if any record exists in riak but not in hitap delete it
                    personel.save()
                    self.logger.info("personel saved.")

                except IndexError:
                    personel = Personel()
                    personel.pno = tckn
                    for record_id, record_values in hitap_dict.items():
                        pass_service_records(personel, record_values)
                        personel.save()
                        self.logger.info("personel saved.")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
