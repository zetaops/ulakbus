# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Banka Borç Sorgulama

Banka tarafından öğrencinin borçlarını sorgulamak için kullanılan Zato Servisi.

Yetkilendirme için banka bilgileri,
öğrenci borç bilgilerine erişim için öğrenci numarası alınır.

Elde edilen bilgilerle öğrencinin tüm borç bilgileri (mevcutsa) listelenir.

Example:
    Servise JSON nesnesi kullanılarak istek gönderilmesi::

        $ curl http://localhost:11223/banka-borc-getir -d
            '{"banka_kodu": "kod", "bank_username": "user", "bank_password": "pass",
            "ogrenci_no":"ogr_no", "sube_kodu":"sube", "kanal_kodu":"kanal", "mesaj_no":"mesaj"}'


"""

from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc
from pyoko.exceptions import ObjectDoesNotExist
import json
from datetime import date


class BankaBorcGetir(BankaService):
    """
    Banka servisinden kalıtılarak gerçekleştirilen Banka Borç Sorgulama servisi.

    """

    def __init__(self):
        super(BankaBorcGetir, self).__init__()

    class SimpleIO():
        """
        Servis girdilerinin ve çıktılarının belirlendiği yapı.

        Attributes:
            borc_request (str): Servise gelen istek yapısının kök elemanının ismi
            borc_response (str): Servisten dönen veriyi içeren (payload) yapının
                                kök elemanının ismi

            banka_kodu (str): Üniversite tarafından bankaya verilen kod
            bank_username (str): Üniversite tarafından bankaya verilen kullanıcı adı
            bank_password (str): Üniversite tarafından bankaya verilen şifre
            sube_kodu (str): Bankaların şubeleri için hali hazırda kullandıkları kodlar
            kanal_kodu (str): G (Gişe), İ (İnternet), A (ATM), T (AloBanka) vb.
            mesaj_no (str): Banka tarafından üretilen kod.
            ogrenci_no (str): Borçları sorgulanan öğrencinin numarası

            mesaj_statusu (str): K (Kabul), R (Ret)
            hata_mesaji (str): Hata mesajı içeriği veya null
            ad_soyad (str): Öğrenci adı soyadı
            ucret_turu (int): Borcun ne için ödeneceği
            tahakkuk_referans_no (str): Her tahakkuka verilen referans numarası
            son_odeme_tarihi (str): Borcun son ödeme tarihi (DDMMYY formatında)
            borc (float): Borcun miktarı
            borc_ack (str): Borç açıklaması

        """

        request_elem = 'borc_request'
        response_elem = 'borc_response'
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                          'ogrenci_no')
        output_required = ('mesaj_statusu','hata_mesaj')
        output_optional = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username', 'bank_password',
                           'ogrenci_no', 'ad_soyad', 'ucret_turu', 'tahakkuk_referans_no', 'son_odeme_tarihi',
                           'borc', 'borc_ack')

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Yetkilendirme işleminin sonucuna göre servis çalışmaya devam eder.

        """

        super(BankaBorcGetir, self).handle()

    def get_data(self):
        """
        Öğrencinin bilgilerine göre tüm borç bilgilerini döndürür.

        Öğrenci numarasına göre, öğrencinin dahil olduğu programdan bilgileri alınır ve
        öğrenciye ait (varsa) borçlara erişilir. Borçlar bir liste halinde geriye döndürülür.

        Öğrenci sistemde bulunamadıysa veya beklenmeyen bir hatayla karşılaşıldıysa
        cevap olarak hata mesajı döndürülür.

        Raises:
            ObjectDoesNotExist: Öğrenci numarası sistemde kayıtlı değildir.
            Exception: Öğrencinin borçları sorgulanırken hatayla karşılaşılmıştır.

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
                    'mesaj_statusu': 'K',
                    'hata_mesaj': None
                }

                self.logger.info("Borc bilgisi: %s" % json.dumps(borc_response))
                self.response.payload.append(borc_response)

        except ObjectDoesNotExist:
            self.logger.info("Ogrenci numarasi bulunamadi.")
            self.response.payload['mesaj_statusu'] = "R"
            self.response.payload['hata_mesaj'] = "Ogrenci numarasi bulunamadi!"
        except Exception as e:
            self.logger.info("Borc sorgulama sirasinda hata olustu: %s" % e)
            self.response.payload['mesaj_statusu'] = "R"
            self.response.payload['hata_mesaj'] = "Borc sorgulama hatasi!"

