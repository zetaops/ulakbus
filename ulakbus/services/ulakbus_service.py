# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
from pyoko.lib.utils import un_camel


class UlakbusService(Service):
    @classmethod
    def get_name(cls):
        return un_camel(cls.__name__, dash='-')


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
        pass

    @classmethod
    def create_hitap_json(cls, data):
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
