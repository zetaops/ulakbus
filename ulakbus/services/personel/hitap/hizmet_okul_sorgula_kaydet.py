# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os, urllib2
from time import sleep
import socket

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.hitap import HizmetOkul

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetOkulSorgula(Service):
    """
    HITAP HizmetOkulSorgula Zato Servisi
    """

    def handle(self):

        def pass_okul_kayitlari(okul_kayitlari_passed, record_values):
            okul_kayitlari_passed.bolum = record_values['bolum']
            okul_kayitlari_passed.kayit_no = record_values['kayit_no']
            okul_kayitlari_passed.mezuniyet_tarihi = record_values['mezuniyet_tarihi']
            okul_kayitlari_passed.ogrenim_suresi = record_values['ogrenim_suresi']
            okul_kayitlari_passed.ogrenim_durumu = record_values['ogrenim_durumu']
            okul_kayitlari_passed.okul_ad = record_values['okul_ad']
            okul_kayitlari_passed.tckn = record_values['tckn']
            okul_kayitlari_passed.denklik_tarihi = record_values['denklik_tarihi']
            okul_kayitlari_passed.ogrenim_yer = record_values['ogrenim_yer']
            okul_kayitlari_passed.denklik_bolum = record_values['denklik_bolum']
            okul_kayitlari_passed.denklik_okul = record_values['denklik_okul']
            okul_kayitlari_passed.hazirlik = record_values['hazirlik']
            okul_kayitlari_passed.kurum_onay_tarihi = record_values['kurum_onay_tarihi']

            self.logger.info("okul_kayitlari successfully passed.")

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetOkulSorgula(H_USER, H_PASS,
                                                                tckn).HizmetEgitimOkulServisBean
                self.logger.info("zato service started to work.")

                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    self.logger.info("Trying to create hitap_dict.")
                    hitap_dict[service_bean[record].kayitNo] = {
                        'bolum': service_bean[record].bolum,
                        'mezuniyet_tarihi': '01.01.1900' if
                        service_bean[record].mezuniyetTarihi == "01.01.0001" else service_bean[
                            record].mezuniyetTarihi,
                        'denklik_tarihi': '01.01.1900' if
                        service_bean[record].denklikTarihi == "01.01.0001" else service_bean[
                            record].denklikTarihi,
                        'kayit_no': service_bean[record].kayitNo,
                        'ogrenim_durumu': service_bean[record].ogrenimDurumu,
                        'ogrenim_suresi': service_bean[record].ogrenimSuresi,
                        'okul_ad': service_bean[record].okulAd,
                        'tckn': service_bean[record].tckn,
                        'ogrenim_yer': service_bean[record].ogrenimYer,
                        'denklik_bolum': service_bean[record].denklikBolum,
                        'denklik_okul': service_bean[record].denklikOkul,
                        'hazirlik': service_bean[record].hazirlik,
                        'kurum_onay_tarihi': '01.01.1900' if
                        service_bean[record].kurumOnayTarihi == "01.01.0001" else service_bean[
                            record].kurumOnayTarihi
                    }
                self.logger.info("hitap_dict created.")

                # if personel saved before, find that and add new records from hitap to riak
                try:
                    local_records = {}
                    # okul_kayitlari_list = HizmetOkul.objects.filter(tckn=tckn)
                    for record in HizmetOkul.objects.filter(tckn=tckn):
                        local_records[record.kayit_no] = {
                            'bolum': record.bolum,
                            'mezuniyet_tarihi': record.mezuniyet_tarihi,
                            'denklik_tarihi': record.denklik_tarihi,
                            'kayit_no': record.kayit_no,
                            'ogrenim_durumu': record.ogrenim_durumu,
                            'ogrenim_suresi': record.ogrenim_suresi,
                            'okul_ad': record.okul_ad,
                            'ogrenim_yer': record.ogrenim_yer,
                            'denklik_bolum': record.denklik_bolum,
                            'denklik_okul': record.denklik_okul,
                            'hazirlik': record.hazirlik,
                            'tckn': record.tckn,
                            'kurum_onay_tarihi': record.kurum_onay_tarihi,
                        }
                    self.logger.info("local_records created.")

                    for record_id, record_values in hitap_dict.items():
                        if record_id in local_records:
                            okul_kayitlari = HizmetOkul.objects.filter(
                                kayit_no=record_id).get()
                            okul_kayitlari.sync = 1
                        else:
                            okul_kayitlari = HizmetOkul()
                            pass_okul_kayitlari(okul_kayitlari, record_values)
                            okul_kayitlari.sync = 1
                        okul_kayitlari.save()

                    for record_id, record_values in local_records.items():
                        okul_kayitlari = HizmetOkul.objects.filter(
                            kayit_no=record_id).get()
                        if record_id not in hitap_dict:
                            if okul_kayitlari.sync == 1:
                                okul_kayitlari.sync = 2
                            if okul_kayitlari.sync == 2:
                                okul_kayitlari.sync = 3

                    self.logger.info("Service runned.")

                except IndexError:
                    okul_kayitlari = HizmetOkul()
                    for hitap_keys, hitap_values in hitap_dict.items():
                        pass_okul_kayitlari(okul_kayitlari, hitap_values)
                        okul_kayitlari.save()
                        self.logger.info("New HizmetOkul saved.")
                    sleep(1)
                except socket.error:
                    self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")
