# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Banka Borç Sorgulama

Banka tarafından öğrencinin borçlarını sorgulamak için kullanılan Zato Servisi.

Yetkilendirme için banka bilgileri,
öğrenci borç bilgilerine erişim için öğrenci numarası verilir.

Elde edilen bilgilerle öğrencinin tüm borç bilgileri (mevcutsa) listelenir.

Example:

    Servise JSON nesnesi kullanılarak istek gönderilmesi:

    .. code-block:: json

        $ curl http://localhost:11223/banka-borc-getir -d '{
            "banka_kodu": "kod",
            "bank_username": "user",
            "bank_password": "pass",
            "ogrenci_no":"1234567890",
            "sube_kodu":"sube",
            "kanal_kodu":"kanal",
            "mesaj_no":"mesaj"
            }'


    İsteğe dönen cevap:

    .. code-block:: json

        $ {"borc_response": [{
            "tahakkuk_referans_no": "tahakkuk",
            "ucret_turu": 1,
            "ad_soyad": "Ad Soyad",
            "bank_password": "pass",
            "bank_username": "user",
            "mesaj_no": "mesaj",
            "sube_kodu": "sube",
            "hata_mesaj": null,
            "borc_ack": "aciklama",
            "son_odeme_tarihi": "07122015",
            "ogrenci_no": "1234567890",
            "banka_kodu": "kod",
            "borc": 214.0,
            "kanal_kodu": "kanal",
            "mesaj_statusu": "K"
            },
            ...
        ]}


    Servise XML kullanılarak istek gönderilmesi:

    .. code-block:: xml

        $ curl http://localhost:11223/banka-borc.banka-borc-getir
            -H "SOAPAction:banka-borc.banka-borc-getir"
            -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:zato="https://zato.io/ns/20130518">
                    <soapenv:Body>
                        <zato:borc_request>
                            <zato:banka_kodu>kod</zato:banka_kodu>
                            <zato:bank_username>user</zato:bank_username>
                            <zato:bank_password>pass</zato:bank_password>
                            <zato:ogrenci_no>1234567890</zato:ogrenci_no>
                            <zato:sube_kodu>sube</zato:sube_kodu>
                            <zato:kanal_kodu>kanal</zato:kanal_kodu>
                            <zato:mesaj_no>mesaj</zato:mesaj_no>
                        </zato:borc_request>
                    </soapenv:Body>
                </soapenv:Envelope>'


    İsteğe dönen cevap:

    .. code-block:: xml

        $ <?xml version='1.0' encoding='UTF-8'?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns="https://zato.io/ns/20130518">
            <soap:Body>
                <borc_response>
                    <zato_env>
                        <cid>K068TA34MK4E0KPWMW1EK5HS9TB8</cid>
                        <result>ZATO_OK</result>
                    </zato_env>
                    <item_list xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
                        <item>
                            <mesaj_statusu>K</mesaj_statusu>
                            <hata_mesaj xsi:nil="true"/>
                            <banka_kodu>kod</banka_kodu>
                            <sube_kodu>sube</sube_kodu>
                            <kanal_kodu>kanal</kanal_kodu>
                            <mesaj_no>mesaj</mesaj_no>
                            <bank_username>user</bank_username>
                            <bank_password>pass</bank_password>
                            <ogrenci_no>1234567890</ogrenci_no>
                            <ad_soyad>Ad Soyad</ad_soyad>
                            <ucret_turu>1</ucret_turu>
                            <tahakkuk_referans_no>tahakkuk</tahakkuk_referans_no>
                            <son_odeme_tarihi>07122015</son_odeme_tarihi>
                            <borc>214.0</borc>
                            <borc_ack>aciklama</borc_ack>
                        </item>
                        <item>
                            ...
                        </item>
                        ...
                    </item_list>
                </borc_response>
            </soap:Body>
        </soap:Envelope>

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

    HAS_CHANNEL = True

    def __init__(self):
        super(BankaBorcGetir, self).__init__()

    class SimpleIO():
        """
        Servis girdilerinin ve çıktılarının belirlendiği yapı.

        Note:
            SimpleIO sınıfında belirlenen özellikler,
            doğrudan yer aldığı servisin özellikleri olmaktadır.

            - borc_request (str): Servise gelen isteğin (JSON, XML) ismi
            - borc_response (str): Servisten dönen veriyi içeren (payload)
              cevabın (JSON, XML) ismi
            - banka_kodu (str): Üniversite tarafından bankaya verilen kod
            - bank_username (str): Üniversite tarafından bankaya verilen kullanıcı adı
            - bank_password (str): Üniversite tarafından bankaya verilen şifre
            - sube_kodu (str): Bankaların şubeleri için hali hazırda kullandıkları kodlar
            - kanal_kodu (str): G (Gişe), İ (İnternet), A (ATM), T (AloBanka) vb.
            - mesaj_no (str): Banka tarafından üretilen kod.
            - ogrenci_no (str): Borçları sorgulanan öğrencinin numarası
            - mesaj_statusu (str): K (Kabul), R (Ret)
            - hata_mesaji (str): Hata mesajı içeriği veya null
            - ad_soyad (str): Öğrenci adı soyadı
            - ucret_turu (int): Borcun ne için ödeneceği
            - tahakkuk_referans_no (str): Her tahakkuka verilen referans numarası
            - son_odeme_tarihi (str): Borcun son ödeme tarihi (DDMMYY formatında)
            - borc (float): Borcun miktarı
            - borc_ack (str): Borç açıklaması

        """

        request_elem = 'borc_request'
        response_elem = 'borc_response'
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username',
                          'bank_password', 'ogrenci_no')
        output_required = ('mesaj_statusu','hata_mesaj')
        output_optional = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username',
                           'bank_password', 'ogrenci_no', 'ad_soyad', 'ucret_turu',
                           'tahakkuk_referans_no', 'son_odeme_tarihi', 'borc', 'borc_ack')

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

        inp = self.request.input

        try:
            ogrenci = OgrenciProgram.objects.get(ogrenci_no=inp.ogrenci_no).ogrenci

            borclar = Borc.objects.filter(ogrenci=ogrenci)
            for borc in borclar:
                borc_response = {
                    'banka_kodu': inp.banka_kodu,
                    'sube_kodu': inp.sube_kodu,
                    'kanal_kodu': inp.kanal_kodu,
                    'mesaj_no': inp.mesaj_no,
                    'bank_username': inp.bank_username,
                    'bank_password': inp.bank_password,
                    'ogrenci_no': inp.ogrenci_no,
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
            self.logger.exception("Ogrenci numarasi bulunamadi.")
            self.response.payload['mesaj_statusu'] = "R"
            self.response.payload['hata_mesaj'] = "Ogrenci numarasi bulunamadi!"
        except Exception:
            self.logger.exception("Borc sorgulama sirasinda hata olustu.")
            self.response.payload['mesaj_statusu'] = "R"
            self.response.payload['hata_mesaj'] = "Borc sorgulama hatasi!"

