# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os
import urllib2

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.employee import Employee

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetNufusSorgula(Service):
    """
    HITAP HizmetNufusSorgula Zato Servisi
    """

    def handle(self):

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        hitap_dict = {}
        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetNufusSorgula(H_USER, H_PASS, tckn)
                self.logger.info("zato service started to work.")

                # collects data from HITAP
                hitap_dict['nufus_sorgula'] = {
                    'tckn': service_bean.tckn,
                    'ad': service_bean.ad,
                    'soyad': service_bean.soyad,
                    'ilk_soy_ad': service_bean.ilkSoyad,
                    'dogum_tarihi': service_bean.dogumTarihi,
                    'cinsiyet': service_bean.cinsiyet,
                    'emekli_sicil_no': service_bean.emekliSicilNo,
                    'memuriyet_baslama_tarihi': service_bean.memuriyetBaslamaTarihi,
                    'kurum_sicil': service_bean.kurumSicili,
                    'maluliyet_kod': service_bean.maluliyetKod,
                    'yetki_seviyesi': service_bean.yetkiSeviyesi,
                    'aciklama': service_bean.aciklama,
                    'kuruma_baslama_tarihi': service_bean.kurumaBaslamaTarihi,
                    'emekli_sicil_6495': service_bean.emekliSicil6495,
                    'gorev_tarihi_6495': '01.01.1900' if
                    service_bean.gorevTarihi6495 == "01.01.0001" else service_bean.gorevTarihi6495,
                    'durum': service_bean.durum,
                    'sebep': service_bean.sebep
                }
                self.logger.info("hitap_dict created.")

                self.logger.info("Trying to find object in db if it not exist create.")
                employee, new = Employee.objects.get_or_create(hitap_dict['nufus_sorgula'],
                                                               nufus_kayitlari__tckn=tckn)
                if new:
                    self.logger.info("Personel not found in db. New created.")
                    employee.NufusKayitlari(hitap_dict['nufus_sorgula'])
                if not new:
                    self.logger.info("Personel also in db.")

                employee.save()
                self.logger.info("Nufus kayitlari successfully saved.")
                self.logger.info("RIAK KEY: %s " % employee.key)

        except AttributeError:
            self.logger.info("TCKN should be wrong!")

        except urllib2.URLError:
            self.logger.info("No internet connection!")
