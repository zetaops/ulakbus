# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os, urllib2
from time import sleep
import socket

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Personel

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetAskerlikSorgula(Service):
    """
    HITAP HizmetAskerlikSorgula Zato Servisi
    """

    def handle(self):

        def pass_askerlik_kayitlari(personel, record_values):
            askerlik_kaytlari = personel.AskerlikKayitlari()
            askerlik_kaytlari.tckn = record_values['tckn']
            askerlik_kaytlari.ad = record_values['ad']
            askerlik_kaytlari.soyad = record_values['soyad']
            askerlik_kaytlari.ilkSoyad = record_values['ilkSoyad']
            askerlik_kaytlari.dogumTarihi = record_values['dogumTarihi']
            askerlik_kaytlari.cinsiyet = record_values['cinsiyet']
            askerlik_kaytlari.emekliSicilNo = record_values['emekliSicilNo']
            askerlik_kaytlari.memuriyetBaslamaTarihi = record_values['memuriyetBaslamaTarihi']
            askerlik_kaytlari.kurumSicil = record_values['kurumSicili']
            askerlik_kaytlari.maluliyetKod = record_values['maluliyetKod']
            askerlik_kaytlari.yetkiSeviyesi = record_values['yetkiSeviyesi']
            askerlik_kaytlari.aciklama = record_values['aciklama']
            askerlik_kaytlari.kurumaBaslamaTarihi = record_values['kurumaBaslamaTarihi']
            askerlik_kaytlari.gorevTarihi6495 = record_values['gorevTarihi6495']
            askerlik_kaytlari.emekliSicil6495 = record_values['emekliSicil6495']
            askerlik_kaytlari.durum = record_values['durum']
            askerlik_kaytlari.sebep = record_values['sebep']

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
                hitap_dict['askerlik_sorgula'] = {
                    'askerlikNevi' : service_bean.askerlikNevi,
                    'baslamaTarihi' : service_bean.baslamaTarihi,
                    'bitisTarihi' : service_bean.bitisTarihi,
                    'kayitNo' : service_bean.kayitNo,
                    'kitaBaslamaTarihi' : service_bean.kitaBaslamaTarihi,
                    'kitaBitisTarihi' : service_bean.kitaBitisTarihi,
                    'muafiyetNeden' : service_bean.muafiyetNeden,
                    'sayilmayanGunSayisi' : service_bean.sayilmayanGunSayisi,
                    'sinifOkuluSicil' : service_bean.sinifOkuluSicil,
                    'subayliktanErligeGecisTarihi' : service_bean.subayliktanErligeGecisTarihi,
                    'subayOkuluGirisTarihi' : service_bean.subayOkuluGirisTarihi,
                    'tckn' : service_bean.tckn,
                    'tegmenNaspTarihi' : service_bean.tegmenNaspTarihi,
                    'gorevYeri' : service_bean.gorevYeri,
                    'kurumOnayTarihi' : service_bean.kurumOnayTarihi,
                    'astegmenNaspTarihi' : service_bean.astegmenNaspTarihi
                }
                self.logger.info("hitap_dict created.")

                # if employee saved before, find that and add new records from hitap to riak
                try:
                    riak_dict_from_db_queries_with_pno = {}
                    personel = Personel.objects.filter(pno=tckn).get()
                    for record in personel.AskerlikKayitlari:
                        riak_dict_from_db_queries_with_pno[record.record_id] = {
                            'askerlikNevi' : record.askerlikNevi,
                            'baslamaTarihi' : record.baslamaTarihi,
                            'bitisTarihi' : record.bitisTarihi,
                            'kayitNo' : record.kayitNo,
                            'kitaBaslamaTarihi' : record.kitaBaslamaTarihi,
                            'kitaBitisTarihi' : record.kitaBitisTarihi,
                            'muafiyetNeden' : record.muafiyetNeden,
                            'sayilmayanGunSayisi' : record.sayilmayanGunSayisi,
                            'sinifOkuluSicil' : record.sinifOkuluSicil,
                            'subayliktanErligeGecisTarihi' : record.subayliktanErligeGecisTarihi,
                            'subayOkuluGirisTarihi' : record.subayOkuluGirisTarihi,
                            'tckn' : record.tckn,
                            'tegmenNaspTarihi' : record.tegmenNaspTarihi,
                            'gorevYeri' : record.gorevYeri,
                            'kurumOnayTarihi' : record.kurumOnayTarihi,
                            'astegmenNaspTarihi' : record.astegmenNaspTarihi
                        }

                    self.logger.info("riak_dict_from_db_queries_with_pno created.")

                    for item in personel.AskerlikKayitlari:
                        if not hitap_dict.has_key(item.record_id):
                            self.logger.info("item key: %s " % (item.record_id))
                            item.remove()
                            self.logger.info("Service record deleted.")

                    for hitap_key, hitap_values in hitap_dict.items():
                        if not riak_dict_from_db_queries_with_pno.has_key(hitap_key):
                            pass_askerlik_kayitlari(personel, hitap_values)

                    # if any record exists in riak but not in hitap delete it
                    personel.save()
                    self.logger.info("personel saved.")

                except IndexError:
                    personel = Personel()
                    personel.pno = tckn
                    for record_id, record_values in hitap_dict.items():
                        pass_askerlik_kayitlari(personel, record_values)
                        personel.save()
                        self.logger.info("personel saved.")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
