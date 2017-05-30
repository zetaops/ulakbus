# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import urllib2

from ulakbus.services.ulakbus_service import UlakbusService


class ZatoHitapService(UlakbusService):

    service_dict = {}

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Servise gelen istekten kimlik numarası (tckn) bilgisini alır ve
        soap outgoing bağlantısını oluşturur. Bu bilgilerle
        Hitap'a gidecek isteği hazırlayacak ve gelen cevabı elde edecek olan
        request_json fonksiyonunu çağırır.

        """

        self.logger.info("zato service started to work.")
        request_payload = self.request.payload
        conn = self.outgoing.soap['HITAP'].conn
        self.request_json(conn, request_payload)

    def request_json(self, conn, request_payload):
        """
            Çalışan iş akışı ve servisine ait servis ismini alarak
            zato ilgili servis objesini getirir.

            Örnek(Kurs Bilgiler İş Akışı):
                request_data = client.factory.create("HizmetKursInsert")
                request_data -> (HizmetKursInsert){
                                   hizmetEgitimKurs =
                                      (HizmetEgitimKursServisBean){
                                         kayitNo = None
                                         kursNevi = None
                                         kursOgrenimSuresi = None
                                         mezuniyetTarihi = None
                                         ogrenimYeri = None
                                         okulAd = None
                                         bolumAd = None
                                         tckn = None
                                         denklikTarihi = None
                                         denklikBolum = None
                                         denklikOkul = None
                                         kurumOnayTarihi = None
                                      }
                                   kullaniciAd = None
                                   sifre = None
                                 }
                olarak doner. Buradaki ilk veri bean nesnesidir. Ekleme ve Güncelleme
                servislerinde bulunur. Sil ve Sync servislerinde ise bean nesnesi bulunmaz.

                Sil servisinin request_data'sı -> (HizmetKursDelete){
                                                               kayitNo = None
                                                               tckn = None
                                                               kullaniciAd = None
                                                               sifre = None}
                şeklindedir.

            iş akışından gönderdiğimiz request_payload nesnesi ile de buradaki gerekli
            yerleri doldururuz.


            gönderdiğimiz verileri ekledikten sonra hitap servisine gönderiyoruz.Bu işlemin
            sonucundan sonra ise hitap bize response datası gönderiyor.

            hitap_service = getattr(client.service, "HizmetKursInsert")(request_data)

            hitap_service -> (ServisSonuc){
                                           hataKod = None
                                           hataMesaj = None
                                           kayitNo = 123
                                         }
            türünde hitaptan bilgi döner. Dönen sonuc dict formatına dönüştürülüp işlem
            sonlandırılır.

        Args:
            conn: Soap connection
            request_payload:(json) İş akışı ile hitap servise gönderdiğimiz bilgiler.

        Returns:

        """
        status = "error"
        hitap_service = {}
        service_name = self.service_dict['service_name']
        try:
            # connection for hitap
            with conn.client() as client:
                self.logger.info("Service name: %s" % service_name)

                request_data = client.factory.create(service_name)

                # filtering for some fields
                if 'date_filter' in self.service_dict:
                    self.date_filter_ulakbus_to_hitap(self.service_dict['date_filter'],
                                                      request_payload)

                if 'required_fields' in self.service_dict:
                    self.check_required_fields(request_payload)

                for field, bean in request_data:
                    if bean:
                        for key, value in self.service_dict['fields'].items():
                            setattr(bean, key, request_payload[value])
                    elif field in self.service_dict['fields']:
                        setattr(request_data,
                                field,
                                request_payload[self.service_dict['fields'][field]])

                request_data.kullaniciAd = request_payload['kullanici_ad']
                request_data.sifre = request_payload['kullanici_sifre']

                self.logger.info("Request Data: %s" % request_data)
                hitap_service = getattr(client.service, service_name)(request_data)
                status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        finally:
            self.logger.info("Status: %s, Result: %s" % (status, hitap_service))
            self.response.payload = {'status': status,
                                     'result': self.create_hitap_json(hitap_service)}

    @staticmethod
    def create_hitap_json(data):
        """Ekleme servisinden dönen veriyi JSON formatına döndürür.
        Converts SOAP call result object into JSON

        """
        fields = ['hataKod', 'hataMesaj', 'kayitNo']

        return dict((field, getattr(data, field)) for field in fields)

    def check_required_fields(self, request_payload):
        """Gelen ``service_dict` içindeki ``required_fields`` sözlük listesi içinde belirtilen servis
        tarafında servis tarafında gerekli olarak tanımlanmış alanların hem ``fields`` sözlüğü
        içinde tanımlı olup olmadığını hem de bu alanların değerinin null olmadığını kontrol
        eder.

        Args:
            request_payload (dict) : HITAP servisine gönderilmek üzere hazırlanmış sözlük listesi.

        """
        for required_field in self.service_dict['required_fields']:
            try:
                if not request_payload[self.service_dict['fields'][required_field]]:
                    raise ValueError("required %s field's value is null" % required_field)
            except KeyError:
                raise KeyError("required field %s not found in hitap service dict" % required_field)

    @staticmethod
    def date_filter_ulakbus_to_hitap(date_filter_fields, request_payload):
        """
        Yerel kayıttaki tarih alanlarını HITAP servisine uygun biçime getirir.

        Hitap'ta tarih alanları için ``0001-01-01`` değeri boş değer anlamına
        gelirken, yerelde ``01.01.1900`` şeklindedir.

        Yerelde GG-AA-YYYY formatında tutulurken, HITAP servisi üzerindeki geçerli
        format YYYY-AA-GG şeklindedir.

        Args:
            date_filter_fields (list): Zato servisinde bulunan ve
            tarih formatinda olan field isimleri listesi

            request_payload (dict): gonderilen kayit degerleri

        """
        from datetime import datetime
        for field in date_filter_fields:

            if request_payload[field] == "01.01.1900":
                request_payload[field] = '0001-01-01'
            else:
                date_format = datetime.strptime(request_payload[field], "%d.%m.%Y")
                request_payload[field] = date_format.strftime("%Y-%m-%d")

    @staticmethod
    def date_filter_hitap_to_ulakbus(date_filter_fields, response_payload):
        """
        date_filter_ulakbus_to_hitap metodunun tersi icin gereklidir.

        Args:
            date_filter_fields (list): Zato servisinde bulunan ve
            tarih formatinda olan field isimleri listesi

            response_payload (dict): gonderilen kayit degerleri

        """
        from datetime import datetime
        for field in date_filter_fields:

            if response_payload[field] == "0001-01-01":
                response_payload[field] = '01.01.1900'
            else:
                date_format = datetime.strptime(response_payload[field], "%Y-%m-%d")
                response_payload[field] = date_format.strftime("%d.%m.%Y")

    def long_to_string(self, hitap_dict):

        for field in hitap_dict:
            if field in self.service_dict['long_to_string']:
                hitap_dict[field] = str(hitap_dict[field])
