# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os, urllib2
from time import sleep

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Personel

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetNufusSorgula(Service):
    """
    HITAP HizmetNufusSorgula Zato Servisi
    """

    def handle(self):

        def pass_nufus_kayitlari(personel, record_values):
            nufus_kayitlari = personel.NufusKayitlari()
            nufus_kayitlari.tckn = record_values['tckn']
            nufus_kayitlari.ad = record_values['ad']
            nufus_kayitlari.soyad = record_values['soyad']
            nufus_kayitlari.ilkSoyad = record_values['ilkSoyad']
            nufus_kayitlari.dogumTarihi = record_values['dogumTarihi']
            nufus_kayitlari.cinsiyet = record_values['cinsiyet']
            nufus_kayitlari.emekliSicilNo = record_values['emekliSicilNo']
            nufus_kayitlari.memuriyetBaslamaTarihi = record_values['memuriyetBaslamaTarihi']
            nufus_kayitlari.kurumSicil = record_values['kurumSicili']
            nufus_kayitlari.maluliyetKod = record_values['maluliyetKod']
            nufus_kayitlari.yetkiSeviyesi = record_values['yetkiSeviyesi']
            nufus_kayitlari.aciklama = record_values['aciklama']
            nufus_kayitlari.kurumaBaslamaTarihi = record_values['kurumaBaslamaTarihi']
            nufus_kayitlari.gorevTarihi6495 = record_values['gorevTarihi6495']
            nufus_kayitlari.emekliSicil6495 = record_values['emekliSicil6495']
            nufus_kayitlari.durum = record_values['durum']
            nufus_kayitlari.sebep = record_values['sebep']

            self.logger.info("Nufus kayitlari successfully passed.")

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetNufusSorgula(H_USER, H_PASS, tckn)
                self.logger.info("zato service started to work.")

                # collects data from HITAP {record_id: record_values_belong_to_that_record_id}
                hitap_dict = {}
                hitap_dict['nufus_sorgula'] = {
                    'tckn': service_bean.tckn,
                    'ad': service_bean.ad,
                    'soyad': service_bean.soyad,
                    'ilkSoyad': service_bean.ilkSoyad,
                    'dogumTarihi': service_bean.dogumTarihi,
                    'cinsiyet': service_bean.cinsiyet,
                    'emekliSicilNo': service_bean.emekliSicilNo,
                    'memuriyetBaslamaTarihi': service_bean.memuriyetBaslamaTarihi,
                    'kurumSicili': service_bean.kurumSicili,
                    'maluliyetKod': service_bean.maluliyetKod,
                    'yetkiSeviyesi': service_bean.yetkiSeviyesi,
                    'aciklama': service_bean.aciklama,
                    'kurumaBaslamaTarihi': service_bean.kurumaBaslamaTarihi,
                    'emekliSicil6495': service_bean.emekliSicil6495,
                    'gorevTarihi6495': service_bean.gorevTarihi6495,
                    'durum': service_bean.durum,
                    'sebep': service_bean.sebep
                }
                self.logger.info("hitap_dict created.")

                try:
                    riak_dict_from_db_queries_with_pno = {}
                    self.logger.info("Trying to find object in db.")
                    personel = Personel.objects.filter(nufus_kayitlari__tckn=tckn).get()
                    pass_nufus_kayitlari(personel, hitap_dict['nufus_sorgula'])
                    personel.save()
                    self.logger.info("Nufus kayitlari successfully saved.")
                    self.logger.info("RIAK KEY: %s " % personel.key)
                    # self.logger.info("Generating dict from riak db.")

                    '''
                    riak_dict_from_db_queries_with_pno['nufus_sorgula'] = {
                        'tckn': nufus_kayitlari.pno,
                        'ad': nufus_kayitlari.first_name,
                        'soyad': nufus_kayitlari.last_name,
                        'ilkSoyad': nufus_kayitlari.first_surname,
                        'dogumTarihi': nufus_kayitlari.birth_date,
                        'cinsiyet': nufus_kayitlari.gender,
                        'emekliSicilNo': nufus_kayitlari.retirement_no,
                        'memuriyetBaslamaTarihi': nufus_kayitlari.job_start_date,
                        'kurumSicili': nufus_kayitlari.corporation_registry,
                        'maluliyetKod': nufus_kayitlari.invalidity_code,
                        'yetkiSeviyesi': nufus_kayitlari.authorisation_level,
                        'aciklama': nufus_kayitlari.explanation,
                        'kurumaBaslamaTarihi': nufus_kayitlari.kuruma_baslam_tarihi,
                        'emekliSicil6495': nufus_kayitlari.retirement_registry6495,
                        'gorevTarihi6495': nufus_kayitlari.duty_time6495,
                        'durum': nufus_kayitlari.status,
                        'sebep': nufus_kayitlari.reason
                    }
                    '''

                    self.logger.info("riak_dict_from_db_queries_with_pno created.")

                except:
                    self.logger.info("Personel not found in RIAK DB.")
                    self.logger.info("New personel created.")
                    personel = Personel()
                    personel.tckn = tckn
                    pass_nufus_kayitlari(personel, hitap_dict['nufus_sorgula'])
                    personel.save()
                    self.logger.info("Nufus kayitlari successfully saved.")
                    self.logger.info("RIAK KEY: %s " % personel.key)
                sleep(1)
                # sleep 1 second

        except AttributeError:
            self.logger.info("TCKN should be wrong!")

        except urllib2.URLError:
            self.logger.info("No internet connection!")
            # LAST LINE