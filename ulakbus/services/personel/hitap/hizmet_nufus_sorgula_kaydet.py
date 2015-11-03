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
from pyoko.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Personel

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetNufusSorgula(Service):
    def handle(self):

        def pass_nufus_kayitlari(nufus_kayitlari_passed, record_values):
            nufus_kayitlari_passed.tckn = record_values['tckn']
            nufus_kayitlari_passed.ad = record_values['ad']
            nufus_kayitlari_passed.soyad = record_values['soyad']
            nufus_kayitlari_passed.ilk_soy_ad = record_values['ilk_soy_ad']
            nufus_kayitlari_passed.dogum_tarihi = record_values['dogum_tarihi']
            nufus_kayitlari_passed.cinsiyet = record_values['cinsiyet']
            nufus_kayitlari_passed.emekli_sicil_no = record_values['emekli_sicil_no']
            nufus_kayitlari_passed.memuriyet_baslama_tarihi = record_values['memuriyet_baslama_tarihi']
            nufus_kayitlari_passed.kurum_sicil = record_values['kurum_sicil']
            nufus_kayitlari_passed.maluliyet_kod = record_values['maluliyet_kod']
            nufus_kayitlari_passed.yetki_seviyesi = record_values['yetki_seviyesi']
            nufus_kayitlari_passed.aciklama = record_values['aciklama']
            nufus_kayitlari_passed.kuruma_baslama_tarihi = record_values['kuruma_baslama_tarihi']
            nufus_kayitlari_passed.emekli_sicil_6495 = record_values['emekli_sicil_6495']
            nufus_kayitlari_passed.gorev_tarihi_6495 = record_values['gorev_tarihi_6495']
            nufus_kayitlari_passed.durum = record_values['durum']
            nufus_kayitlari_passed.sebep = record_values['sebep']

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

                try:
                    personel = Personel.objects.filter(nufus_kayitlari__tckn=service_bean.tckn).get()
                    new = False
                except ObjectDoesNotExist:
                    new = True
                if new:
                    self.logger.info("Personel not found in db. New created.")
                    personel = Personel()
                    nufus_kayitlari = personel.NufusKayitlari()
                    pass_nufus_kayitlari(nufus_kayitlari, hitap_dict['nufus_sorgula'])

                    nufus_kayitlari.sync = 1
                    personel.save()

                if not new and personel.NufusKayitlari.sync != 1:
                    self.logger.info("Personel also in db. But not up to date.")
                    nufus_kayitlari = Personel()
                    pass_nufus_kayitlari(nufus_kayitlari, hitap_dict['nufus_sorgula'])

                    nufus_kayitlari.sync = 1
                    personel.save()
                if not new and personel.NufusKayitlari.sync == 1:
                    self.logger.info("Nufus kayitlari is up to date also.")

                self.logger.info("Nufus kayitlari successfully saved.")
                self.logger.info("RIAK KEY: %s " % personel.key)

        except AttributeError:
            self.logger.info("TCKN should be wrong!")

        except urllib2.URLError:
            self.logger.info("No internet connection!")
