# -*-  coding: utf-8 -*-
"""
    HITAP HizmetNufusSorgula Zato Servisi
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
import os
import urllib2

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Personel

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetNufusSorgula(Service):
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
                self.logger.info("TCKN : %s" % hitap_dict['nufus_sorgula']['tckn'])

                self.logger.info("Trying to find object in db if it not exist create.")
                personel, new = Personel.objects.get_or_create(None, tckn=service_bean.tckn)
                if new:
                    self.logger.info("Personel not found in db. New created.")

                    personel.NufusKayitlari(hitap_dict['nufus_sorgula'])
                    personel.save()

                if not new:
                    self.logger.info("Personel also in db.")
                    personel.NufusKayitlari(hitap_dict['nufus_sorgula'])
                    personel.save()

                    self.logger.info("Personel's NufusKayitlari updated and saved.")

                self.logger.info("Nufus kayitlari successfully saved.")
                self.logger.info("RIAK KEY: %s " % personel.key)

        except AttributeError:
            self.logger.info("TCKN should be wrong!")

        except urllib2.URLError:
            self.logger.info("No internet connection!")
