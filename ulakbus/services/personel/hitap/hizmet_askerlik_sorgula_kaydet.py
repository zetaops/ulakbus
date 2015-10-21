# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os, urllib2
from time import sleep
import socket

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.hitap import AskerlikKayitlari

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetAskerlikSorgula(Service):
    """
    HITAP HizmetAskerlikSorgula Zato Servisi
    """

    def handle(self):

        def pass_askerlik_kayitlari(askerlik_kayitlari_passed, record_values):
            askerlik_kayitlari_passed.askerlik_nevi = record_values['askerlik_nevi']
            askerlik_kayitlari_passed.baslama_tarihi = record_values['baslama_tarihi']
            askerlik_kayitlari_passed.bitis_tarihi = record_values['bitis_tarihi']
            askerlik_kayitlari_passed.kayit_no = record_values['kayit_no']
            askerlik_kayitlari_passed.kita_baslama_tarihi = record_values['kita_baslama_tarihi']
            askerlik_kayitlari_passed.kita_bitis_tarihi = record_values['kita_bitis_tarihi']
            askerlik_kayitlari_passed.muafiyet_neden = record_values['muafiyet_neden']
            askerlik_kayitlari_passed.sayilmayan_gun_sayisi = record_values['sayilmayan_gun_sayisi']
            askerlik_kayitlari_passed.sinif_okulu_sicil = record_values['sinif_okulu_sicil']
            askerlik_kayitlari_passed.subayliktan_erlige_gecis_tarihi = record_values[
                'subayliktan_erlige_gecis_tarihi']
            askerlik_kayitlari_passed.subay_okulu_giris_tarihi = record_values[
                'subay_okulu_giris_tarihi']
            askerlik_kayitlari_passed.tckn = record_values['tckn']
            askerlik_kayitlari_passed.tegmen_nasp_tarihi = record_values['tegmen_nasp_tarihi']
            askerlik_kayitlari_passed.gorev_yeri = record_values['gorev_yeri']
            askerlik_kayitlari_passed.kurum_onay_tarihi = record_values['kurum_onay_tarihi']
            askerlik_kayitlari_passed.astegmen_nasp_tarihi = record_values['astegmen_nasp_tarihi']

            self.logger.info("askerlik_kayitlari successfully passed.")

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetAskerlikSorgula(H_USER, H_PASS,
                                                                    tckn).HizmetAskerlikServisBean
                self.logger.info("zato service started to work.")

                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    self.logger.info("Trying to create hitap_dict.")
                    hitap_dict[service_bean[record].kayitNo] = {
                        'askerlik_nevi': service_bean[record].askerlikNevi,
                        'baslama_tarihi': '01.01.1900' if
                        service_bean[record].baslamaTarihi == "01.01.0001" else service_bean[
                            record].baslamaTarihi,
                        'bitis_tarihi': '01.01.1900' if
                        service_bean[record].bitisTarihi == "01.01.0001" else service_bean[
                            record].bitisTarihi,
                        'kayit_no': service_bean[record].kayitNo,
                        'kita_baslama_tarihi': '01.01.1900' if
                        service_bean[record].kitaBaslamaTarihi == "01.01.0001" else service_bean[
                            record].kitaBaslamaTarihi,
                        'kita_bitis_tarihi': '01.01.1900' if
                        service_bean[record].kitaBitisTarihi == "01.01.0001" else service_bean[
                            record].kitaBitisTarihi,
                        'muafiyet_neden': service_bean[record].muafiyetNeden,
                        'sayilmayan_gun_sayisi': service_bean[record].sayilmayanGunSayisi,
                        'sinif_okulu_sicil': service_bean[record].sinifOkuluSicil,
                        'subayliktan_erlige_gecis_tarihi': '01.01.1900' if
                        service_bean[record].subayliktanErligeGecisTarihi == "01.01.0001" else
                        service_bean[record].subayliktanErligeGecisTarihi,
                        'subay_okulu_giris_tarihi': '01.01.1900' if
                        service_bean[record].subayOkuluGirisTarihi == "01.01.0001" else
                        service_bean[record].subayOkuluGirisTarihi,
                        'tckn': service_bean[record].tckn,
                        'tegmen_nasp_tarihi': '01.01.1900' if
                        service_bean[record].tegmenNaspTarihi == "01.01.0001" else service_bean[
                            record].tegmenNaspTarihi,
                        'gorev_yeri': service_bean[record].gorevYeri,
                        'kurum_onay_tarihi': '01.01.1900' if
                        service_bean[record].kurumOnayTarihi == "01.01.0001" else service_bean[
                            record].kurumOnayTarihi,
                        'astegmen_nasp_tarihi': '01.01.1900' if
                        service_bean[record].astegmenNaspTarihi == "01.01.0001" else service_bean[
                            record].astegmenNaspTarihi
                    }
                self.logger.info("hitap_dict created.")

                # if personel saved before, find that and add new records from hitap to riak
                try:
                    local_records = {}
                    # askerlik_kayitlari_list = AskerlikKayitlari.objects.filter(tckn=tckn)
                    for record in AskerlikKayitlari.objects.filter(tckn=tckn):
                        local_records[record.kayit_no] = {
                            'askerlik_nevi': record.askerlik_nevi,
                            'baslama_tarihi': record.baslama_tarihi,
                            'bitis_tarihi': record.bitis_tarihi,
                            'kayit_no': record.kayit_no,
                            'kita_baslama_tarihi': record.kita_baslama_tarihi,
                            'kita_bitis_tarihi': record.kita_bitis_tarihi,
                            'muafiyet_neden': record.muafiyet_neden,
                            'sayilmayan_gun_sayisi': record.sayilmayan_gun_sayisi,
                            'sinif_okulu_sicil': record.sinif_okulu_sicil,
                            'subayliktan_erlige_gecis_tarihi':
                                record.subayliktan_erlige_gecis_tarihi,
                            'subay_okulu_giris_tarihi': record.subay_okulu_giris_tarihi,
                            'tckn': record.tckn,
                            'tegmen_nasp_tarihi': record.tegmen_nasp_tarihi,
                            'gorev_yeri': record.gorev_yeri,
                            'kurum_onay_tarihi': record.kurum_onay_tarihi,
                            'astegmen_nasp_tarihi': record.astegmen_nasp_tarihi
                        }
                    self.logger.info("local_records created.")

                    for record_id, record_values in hitap_dict.items():
                        if record_id in local_records:
                            askerlik_kayitlari = AskerlikKayitlari.objects.filter(
                                kayit_no=record_id).get()
                            askerlik_kayitlari.sync = 1
                        else:
                            askerlik_kayitlari = AskerlikKayitlari()
                            pass_askerlik_kayitlari(askerlik_kayitlari, record_values)
                            askerlik_kayitlari.sync = 1
                        askerlik_kayitlari.save()

                    for record_id, record_values in local_records.items():
                        askerlik_kayitlari = AskerlikKayitlari.objects.filter(
                            kayit_no=record_id).get()
                        if record_id not in hitap_dict:
                            if askerlik_kayitlari.sync == 1:
                                askerlik_kayitlari.sync = 2
                            if askerlik_kayitlari.sync == 2:
                                askerlik_kayitlari.sync = 3

                    self.logger.info("Service runned.")

                except IndexError:
                    askerlik_kayitlari = AskerlikKayitlari()
                    for hitap_keys, hitap_values in hitap_dict.items():
                        pass_askerlik_kayitlari(askerlik_kayitlari, hitap_values)
                        askerlik_kayitlari.save()
                        self.logger.info("New AskerlikKayitlari saved.")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
