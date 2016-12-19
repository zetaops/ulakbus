# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Banka Borç Ödeme

Banka tarafından öğrencinin borçlarını ödemek için kullanılan Zato Servisi.

Yetkilendirme için banka bilgileri,
öğrenci borç ödemesinin gerçekleştirimi için öğrenci numarası ve ödeme bilgileri verilir.

Elde edilen bilgilerle öğrencinin borç ödeme bilgisi sisteme kaydedilir.

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
            "mesaj_no":"mesaj",
            "ucret_turu":1,
            "tahakkuk_referans_no":"tahakkuk",
            "tahsilat_referans_no":"tahsilat",
            "odeme_timestamp":"07122015123456",
            "odeme_tutari":214.0
            }'


    İsteğe dönen cevap:

    .. code-block:: json

        $ {"odeme_response": [{
            "tahakkuk_referans_no": "tahakkuk",
            "odeme_timestamp": "07122015123456",
            "odeme_tutari": "214.0",
            "ucret_turu": 1,
            "tahsilat_referans_no": "tahsilat",
            "bank_password": "pass",
            "bank_username": "user",
            "mesaj_no": "mesaj",
            "sube_kodu": "sube",
            "hata_mesaj": null,
            "ogrenci_no": "1234567890",
            "banka_kodu": "kod",
            "kanal_kodu": "kanal",
            "mesaj_statusu": "K"
            }
        ]}


    Servise XML kullanılarak istek gönderilmesi:

    .. code-block:: xml

        $ curl http://localhost:11223/banka-odeme.banka-borc-odeme
            -H "SOAPAction:banka-odeme.banka-borc-odeme"
            -d '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:zato="https://zato.io/ns/20130518">
                    <soapenv:Body>
                        <zato:odeme_request>
                            <zato:banka_kodu>kod</zato:banka_kodu>
                            <zato:bank_username>user</zato:bank_username>
                            <zato:bank_password>pass</zato:bank_password>
                            <zato:ogrenci_no>1234567890</zato:ogrenci_no>
                            <zato:sube_kodu>sube</zato:sube_kodu>
                            <zato:kanal_kodu>kanal</zato:kanal_kodu>
                            <zato:mesaj_no>mesaj</zato:mesaj_no>
                            <zato:ucret_turu>1</zato:ucret_turu>
                            <zato:tahakkuk_referans_no>tahakkuk</zato:tahakkuk_referans_no>
                            <zato:tahsilat_referans_no>tahsilat</zato:tahsilat_referans_no>
                            <zato:odeme_timestamp>07122015123456</zato:odeme_timestamp>
                            <zato:odeme_tutari>214.0</zato:odeme_tutari>
                        </zato:odeme_request>
                    </soapenv:Body>
                </soapenv:Envelope>'


    İsteğe dönen cevap:

    .. code-block:: xml

        $ <?xml version='1.0' encoding='UTF-8'?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns="https://zato.io/ns/20130518">
            <soap:Body>
                <odeme_response>
                    <zato_env>
                        <cid>K07C4A0D30PHBMBGX18BYAZBZRH7</cid>
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
                            <ucret_turu>1</ucret_turu>
                            <tahakkuk_referans_no>tahakkuk</tahakkuk_referans_no>
                            <tahsilat_referans_no>tahsilat</tahsilat_referans_no>
                            <odeme_timestamp>07122015123456</odeme_timestamp>
                            <odeme_tutari>214.0</odeme_tutari>
                        </item>
                    </item_list>
                </odeme_response>
            </soap:Body>
        </soap:Envelope>

"""

from ulakbus.services.common.banka import BankaService
from ulakbus.models.ogrenci import OgrenciProgram, Borc, Odeme
from pyoko.exceptions import ObjectDoesNotExist
import json
from datetime import datetime


class BankaBorcOdeme(BankaService):
    """
    Banka servisinden kalıtılarak gerçekleştirilen Banka Borç Ödeme servisi

    """

    HAS_CHANNEL = True

    def __init__(self):
        super(BankaBorcOdeme, self).__init__()

    class SimpleIO():
        """
        Servis girdilerinin ve çıktılarının belirlendiği yapı.

        Note:
            SimpleIO sınıfında belirlenen özellikler,
            doğrudan yer aldığı servisin özellikleri olmaktadır.

            - odeme_request (str): Servise gelen isteğin (JSON, XML) ismi
            - odeme_response (str): Servisten dönen veriyi içeren (payload)
              cevabın (JSON, XML) ismi
            - mesaj_statusu (str): K (Kabul), R (Ret)
            - hata_mesaji (str): Hata mesajı içeriği veya null
            - banka_kodu (str): Üniversite tarafından bankaya verilen kod
            - bank_username (str): Üniversite tarafından bankaya verilen kullanıcı adı
            - bank_password (str): Üniversite tarafından bankaya verilen şifre
            - sube_kodu (str): Bankaların şubeleri için hali hazırda kullandıkları kodlar
            - kanal_kodu (str): G (Gişe), İ (İnternet), A (ATM), T (AloBanka) vb.
            - mesaj_no (str): Banka tarafından üretilen kod.
            - ogrenci_no (str): Borçları sorgulanan öğrencinin numarası
            - ucret_turu (int): Borcun ne için ödeneceği
            - tahakkuk_referans_no (str): Her tahakkuka verilen referans numarası
            - tahsilat_referans_no (str): Banka tarafından verilen tahsilata ait referans no
            - odeme_timestamp (str): DDMMYYYYHHMMSS formatında ödeme tarihi
            - odeme_tutari (float): Banka tarafından tahsil edilen tutar

        """

        request_elem = 'odeme_request'
        response_elem = 'odeme_response'
        input_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username',
                          'bank_password', 'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no',
                          'tahsilat_referans_no', 'odeme_timestamp', 'odeme_tutari')
        output_required = ('banka_kodu', 'sube_kodu', 'kanal_kodu', 'mesaj_no', 'bank_username',
                           'bank_password', 'ogrenci_no', 'ucret_turu', 'tahakkuk_referans_no',
                           'tahsilat_referans_no', 'odeme_timestamp', 'odeme_tutari',
                           'mesaj_statusu', 'hata_mesaj')

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Yetkilendirme işleminin sonucuna göre servis çalışmaya devam eder.

        """

        super(BankaBorcOdeme, self).handle()

    def get_data(self):
        """
        Öğrencinin borç ödeme bilgilerini bankadan gelen bilgilere göre sisteme kaydeder.

        Öğrenci numarası ve borcuna ait tahakkuk referans numarasına göre,
        öğrencinin borcuna erişilir. Bankadan gelen ödeme bilgisine göre bu borca ait
        bir ödeme bilgisi oluşturulur.

        Öğrenci sistemde bulunamadıysa veya beklenmeyen bir hatayla karşılaşıldıysa
        cevap olarak hata mesajı döndürülür.

        Raises:
            ObjectDoesNotExist: Öğrenci numarası sistemde kayıtlı değildir.
            Exception: Öğrencinin borç ödeme bilgisi kaydedilirken hatayla karşılaşılmıştır.

        """

        super(BankaBorcOdeme, self).get_data()

        inp = self.request.input
        mesaj_statusu = "R"
        hata_mesaj = None

        try:
            ogrenci_no = inp.ogrenci_no
            ogrenci = OgrenciProgram.objects.get(ogrenci_no=ogrenci_no).ogrenci

            # her borcun referans numarasi olarak 'tahakkuk_referans_no' kullanilir
            borc = Borc.objects.filter(ogrenci=ogrenci,
                                       tahakkuk_referans_no=inp.tahakkuk_referans_no)[0]

            odeme = Odeme()
            odeme.miktar = inp.odeme_tutari
            odeme.para_birimi = 1  # TL
            odeme.aciklama = borc.aciklama
            odeme.odeme_sekli = 3  # Banka
            odeme.odeme_tarihi = datetime.strptime(inp.odeme_timestamp, "%d%m%Y%H%M%S")
            odeme.borc = borc
            odeme.ogrenci = ogrenci
            odeme.banka = self.banka
            odeme.banka_sube_kodu = str(inp.sube_kodu)
            odeme.banka_kanal_kodu = inp.kanal_kodu
            odeme.banka_kanal_kodu = inp.kanal_kodu
            odeme.tahsilat_referans_no = inp.tahsilat_referans_no
            odeme.donem = borc.donem

            odeme.save()
            mesaj_statusu = "K"
            hata_mesaj = None

        except ObjectDoesNotExist:
            self.logger.exception('Ogrenci numarasi bulunamadi.')
            mesaj_statusu = "R"
            hata_mesaj = "Ogrenci numarasi bulunamadi!"

        except Exception:
            self.logger.exception("Odeme kaydedilirken hata olustu.")
            mesaj_statusu = "R"
            hata_mesaj = "Odeme kaydedilirken hata olustu!"

        finally:
            odeme_response = {
                'banka_kodu': inp.banka_kodu,
                'sube_kodu': inp.sube_kodu,
                'kanal_kodu': inp.kanal_kodu,
                'mesaj_no': inp.mesaj_no,
                'bank_username': inp.bank_username,
                'bank_password': inp.bank_password,
                'mesaj_statusu': mesaj_statusu,
                'ogrenci_no': inp.ogrenci_no,
                'ucret_turu': inp.ucret_turu,
                'tahakkuk_referans_no': inp.tahakkuk_referans_no,
                'tahsilat_referans_no': inp.tahsilat_referans_no,
                'odeme_timestamp': inp.odeme_timestamp,
                'odeme_tutari': inp.odeme_tutari,
                'hata_mesaj': hata_mesaj
            }

            self.logger.info("Odeme bilgisi: %s" % json.dumps(odeme_response))
            self.response.payload.append(odeme_response)
