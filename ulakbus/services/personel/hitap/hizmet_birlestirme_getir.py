# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
import os
import urllib2
from json import dumps

# os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
# from ulakbus.models.hitap import HizmetKayitlari

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetBirlestirmeGetir(Service):
    """
    HITAP HizmetBirlestirmeGetir Zato Servisi
    """

    def handle(self):
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                service_bean = client.service.HizmetBirlestirmeSorgula(H_USER, H_PASS,
                                                                  tckn).HizmetBirlestirmeServisBean
                self.logger.info("HizmetBirlestirmeGetir started to work.")

                hitap_dict = {}
                for record in range(0, len(service_bean)):
                    hitap_dict[service_bean[record].kayitNo] = {
                        'kayit_no': service_bean[record].kayitNo,
                        'baslama_tarihi': '01.01.1900' if
                        service_bean[record].baslamaTarihi == "01.01.0001" else
                        service_bean[record].baslamaTarihi,
                        'bitis_tarihi': '01.01.1900' if
                        service_bean[record].bitisTarihi == "01.01.0001" else
                        service_bean[record].bitisTarihi,
                        'sgkNevi': service_bean[record].sgkNevi,
                        'sgkSicilNo': service_bean[record].sgkSicilNo,
                        'sure':service_bean[record].sure,
                        'kamuIsyeriAd':service_bean[record].kamuIsyeriAd,
                        'ozelIsyeriAd':service_bean[record].ozelIsyeriAd,
                        'bagKurMeslek': service_bean[record].bagKurMeslek,
                        'ulkeKod': service_bean[record].ulkeKod,
                        'bankaSandikKod': service_bean[record].bankaSandikKod,
                        'kidemTazminatOdemeDurumu': service_bean[record].kidemTazminatOdemeDurumu,
                        'ayrilmaNedeni': service_bean[record].ayrilmaNedeni,
                        'khaDurum': service_bean[record].khaDurum,
                        'kurumOnayTarihi': service_bean[record].kurumOnayTarihi,
                        'tckn': service_bean[record].tckn
                    }
                self.logger.info("hitap_dict created.")

            response_json = dumps(hitap_dict)
            return_dict = {"status": "ok", "result": response_json}
            # self.response.payload = dumps(return_dict)
            self.response.payload = {"status": "ok", "result": response_json}
            # self.response.payload["status"] = "ok"
            # self.response.payload["result"] = response_json

        except AttributeError:
            self.response.payload["status"] = "error"
            self.response.payload["result"] = "TCKN may be wrong!"
            self.logger.info("TCKN may be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")

    def kidem_tazminat_odeme_durumu(self, kidem_durum):
        """
        Kıdem Tazminat ödeme durumu hitap servisinden aşağıdaki gibi gelmektedir.
        0: HAYIR
        1: EVET
        “”(BOŞ KARAKTER): BELİRLENEMEDİ

        Ulakbus kaydederken BELİRLENEMEDİ = 2 yapılacaktır

        :param hs: hitaptan donen kıdem durumu
        :type hs: str
        :return str: kıdem durumu

        """
        if kidem_durum == "":
            return "2"
        else:
            return str(kidem_durum)
