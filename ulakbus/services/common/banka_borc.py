# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc
from pyoko.exceptions import ObjectDoesNotExist
import json
from datetime import date


class BankaBorcGetir(BankaService):
    """
    Banka Borc Sorgulama Zato Servisi

    :param banka_kodu: Universite tarafindan bankaya verilen kod
    :type banka_kodu: int -> str

    :param bank_username: Universite tarafindan bankaya verilen kullanici kodu
    :type bank_username: str

    :param bank_password: Universite tarafindan bankaya verilen kullanici sifresi
    :type bank_username: str

    :param ogrenci_no: Borclari sorgulanan ogrencinin kayitli oldugu programa ait ogrenci numarasi
    :type sube_kodu: str

    :return Borc bilgilerini liste halinde iceren JSON nesnesi
    """

    def __init__(self):
        super(BankaBorcGetir, self).__init__()

    class SimpleIO():
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                          'ogrenci_no')
        output_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                           'ogrenci_no', 'ad_soyad', 'ucret_turu', 'tahakkuk_referans_no', 'son_odeme_tarihi',
                           'borc', 'borc_ack', 'mesaj_statusu','hata_mesaj')
        output_optional = ('mesaj_statusu','hata_mesaj')

    def handle(self):
        super(BankaBorcGetir, self).handle()

    def get_data(self):
        """
        Ogrencinin borc bilgilerinin dondurulmesi

        :return: Borc bilgilerini liste halinde iceren JSON nesnesi
        """

        super(BankaBorcGetir, self).get_data()

        try:
            ogrenci_no = self.request.input.ogrenci_no
            ogrenci = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no).ogrenci

            borclar = Borc.objects.filter(ogrenci=ogrenci)
            for borc in borclar:
                borc_response = {
                    'banka_kodu': self.request.input.banka_kodu,
                    'sube_kodu': self.request.input.sube_kodu,
                    'kanal_kodu': self.request.input.kanal_kodu,
                    'mesaj_no': self.request.input.mesaj_no,
                    'bank_username': self.request.input.bank_username,
                    'bank_password': self.request.input.bank_password,
                    'ogrenci_no': self.request.input.ogrenci_no,
                    'ad_soyad': ogrenci.ad + " " + ogrenci.soyad,
                    'ucret_turu': borc.sebep,
                    'tahakkuk_referans_no': borc.tahakkuk_referans_no,
                    'son_odeme_tarihi': date.strftime(borc.son_odeme_tarihi, format='%d%m%Y'),
                    'borc': borc.miktar,
                    'borc_ack': borc.aciklama,
                    'mesaj_statusu': 'K', # Kabul edildi
                    'hata_mesaj': None
                }

                self.logger.info("Borc bilgisi: %s" % json.dumps(borc_response))
                self.response.payload.append(borc_response)

        except ObjectDoesNotExist:
            self.logger.info("Ogrenci numarasi bulunamadi.")
            self.response.payload['mesaj_statusu'] = "R"  # Reddedildi
            self.response.payload['hata_mesaj'] = "Ogrenci numarasi bulunamadi!"
        except Exception as e:
            self.logger.info("Borc sorgulama sirasinda hata olustu: %s" % e)
            self.response.payload['hata_mesaj'] = "Borc sorgulama hatasi!"

