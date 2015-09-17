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

        def pass_askerlik_kayitlari(employee, record_values):
            askerlik_kayitlari = employee.AskerlikKayitlari()

            askerlik_kayitlari.askerlik_nevi = record_values['askerlik_nevi']
            askerlik_kayitlari.baslama_tarihi = record_values['baslama_tarihi']
            askerlik_kayitlari.bitis_tarihi = record_values['bitis_tarihi']
            askerlik_kayitlari.kayit_no = record_values['kayit_no']
            askerlik_kayitlari.kita_baslama_tarihi = record_values['kita_baslama_tarihi']
            askerlik_kayitlari.kita_bitis_tarihi = record_values['kita_bitis_tarihi']
            askerlik_kayitlari.muafiyet_neden = record_values['muafiyet_neden']
            askerlik_kayitlari.sayilmayan_gun_sayisi = record_values['sayilmayan_gun_sayisi']
            askerlik_kayitlari.sinif_okulu_sicil = record_values['sinif_okulu_sicil']
            askerlik_kayitlari.subayliktan_erlige_gecis_tarihi = record_values['subayliktan_erlige_gecis_tarihi']
            askerlik_kayitlari.subay_okulu_giris_tarihi = record_values['subay_okulu_giris_tarihi']
            askerlik_kayitlari.tckn = record_values['tckn']
            askerlik_kayitlari.tegmen_nasp_tarihi = record_values['tegmen_nasp_tarihi']
            askerlik_kayitlari.gorev_yeri = record_values['gorev_yeri']
            askerlik_kayitlari.kurum_onay_tarihi = record_values['kurum_onay_tarihi']
            askerlik_kayitlari.astegmen_nasp_tarihi = record_values['astegmen_nasp_tarihi']

            self.logger.info("Nufus kayitlari successfully passed.")

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetAskerlikSorgula(H_USER, H_PASS, tckn)
                self.logger.info("zato service started to work.")

                # collects data from HITAP {record_id: record_values_belong_to_that_record_id}
                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    self.logger.info("Trying to create hitap_dict.")
                    hitap_dict[service_bean[record].kayitNo] = {
                        'askerlik_nevi': service_bean[record].askerlikNevi,
                        'baslama_tarihi': service_bean[record].baslamaTarihi,
                        'bitis_tarihi': service_bean[record].bitisTarihi,
                        'kayit_no': service_bean[record].kayitNo,
                        'kita_baslama_tarihi': service_bean[record].kitaBaslamaTarihi,
                        'kita_bitis_tarihi': service_bean[record].kitaBitisTarihi,
                        'muafiyet_neden': service_bean[record].muafiyetNeden,
                        'sayilmayan_gun_sayisi': service_bean[record].sayilmayanGunSayisi,
                        'sinif_okulu_sicil': service_bean[record].sinifOkuluSicil,
                        'subayliktan_erlige_gecis_tarihi': service_bean[record].subayliktanErligeGecisTarihi,
                        'subay_okulu_giris_tarihi': service_bean[record].subayOkuluGirisTarihi,
                        'tckn': service_bean[record].tckn,
                        'tegmen_nasp_tarihi': service_bean[record].tegmenNaspTarihi,
                        'gorev_yeri': service_bean[record].gorevYeri,
                        'kurum_onay_tarihi': service_bean[record].kurumOnayTarihi,
                        'astegmen_nasp_tarihi': service_bean[record].astegmenNaspTarihi
                    }
                self.logger.info("hitap_dict created.")

                # if employee saved before, find that and add new records from hitap to riak
                try:
                    riak_dict_from_db_queries_with_pno = {}
                    employee = Personel.objects.filter(tckn=tckn).get()
                    for record in employee.AskerlikKayitlari:
                        riak_dict_from_db_queries_with_pno[record.record_id] = {
                            'askerlik_nevi': record.askerlik_nevi,
                            'baslama_tarihi': record.baslama_tarihi,
                            'bitis_tarihi': record.bitis_tarihi,
                            'kayit_no': record.kayit_no,
                            'kita_baslama_tarihi': record.kita_baslama_tarihi,
                            'kita_bitis_tarihi': record.kita_bitis_tarihi,
                            'muafiyet_neden': record.muafiyet_neden,
                            'sayilmayan_gun_sayisi': record.sayilmayan_gun_sayisi,
                            'sinif_okulu_sicil': record.sinif_okulu_sicil,
                            'subayliktan_erlige_gecis_tarihi': record.subayliktan_erlige_gecis_tarihi,
                            'subay_okulu_giris_tarihi': record.subay_okulu_giris_tarihi,
                            'tckn': record.tckn,
                            'tegmen_nasp_tarihi': record.tegmen_nasp_tarihi,
                            'gorev_yeri': record.gorev_yeri,
                            'kurum_onay_tarihi': record.kurum_onay_tarihi,
                            'astegmen_nasp_tarihi': record.astegmen_nasp_tarihi
                        }

                    self.logger.info("riak_dict_from_db_queries_with_pno created.")

                    for item in employee.AskerlikKayitlari:
                        if not hitap_dict.has_key(item.record_id):
                            self.logger.info("item key: %s " % (item.record_id))
                            item.remove()
                            self.logger.info("Service record deleted.")

                    for hitap_key, hitap_values in hitap_dict.items():
                        if not riak_dict_from_db_queries_with_pno.has_key(hitap_key):
                            pass_askerlik_kayitlari(employee, hitap_values)

                    # if any record exists in riak but not in hitap delete it
                    employee.save()
                    self.logger.info("employee saved.")

                except IndexError:
                    employee = Personel()
                    employee.tckn = tckn
                    for record_id, record_values in hitap_dict.items():
                        pass_askerlik_kayitlari(employee, record_values)
                        employee.save()
                        self.logger.info("employee saved.")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
