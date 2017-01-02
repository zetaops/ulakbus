# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
import os
import urllib2
from json import dumps

"""HITAP Sil Servisi

Hitap sil (delete) servislerinin kalıtılacağı
abstract HITAP Sil servisini içeren modül.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi

"""

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPSil(UlakbusService):
    """
    Hitap Silme servislerinin kalıtılacağı abstract Zato servisi.

    Silme servisleri gerekli girdileri (Hitap dict, Hitap username, Hitap password)
    Hitap'a yollayıp dönecek cevabı elde eder.

    Attributes:
        service_name (str): İlgili Hitap sorgu servisinin adı
        service_dict (dict): Hitap servisine yollanacak datayı hazırlamak için sözlük.
            Servise gönderilecek verinin alanlarına ait sözlüğü içerir.

    """
    HAS_CHANNEL = False
    service_dict = {"fields": {}, "service_name": '', 'required_fields': []}

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Hitap'a gidecek isteği hazırlayacak ve gelen cevabı elde edecek olan
        request_json fonksiyonunu çağırır.

        """

        self.logger.info("zato service started to work.")
        conn = self.outgoing.soap['HITAP'].conn
        request_payload = self.request.payload
        self.request_json(conn, request_payload)

    def request_json(self, conn, request_payload):
        """Connection bilgisi ve gerekli veriler ile Hitap'ın ilgili servisine
        istekte bulunup gelen cevabı uygun şekilde elde eder.

        Hitap'tan gelen verilerin sisteme uygun şekilde elde edilmesi için, gerekli
        Hitap sözlüğünü yaratan ve tarih alanı gibi belli alanlara uygun filteleri
        uygulayacak olan fonksiyonları çağırır.

        Veriler uygun şekilde elde edildikten sonra servis cevabı (payload) oluşturulur.

        Args:
            conn (zato.outgoing.soap.conn): Zato soap outgoing bağlantısı

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.

        """

        status = "error"
        hitap_service = ''
        service_name = self.service_dict['service_name']
        try:
            # connection for hitap
            with conn.client() as client:

                request_data = client.factory.create(service_name)

                request_data.kullaniciAd = H_USER
                request_data.sifre = H_PASS

                for dict_element in self.service_dict["fields"]:
                    setattr(request_data, dict_element, request_payload[self.service_dict['fields'][dict_element]])

                if 'required_fields' in self.service_dict:
                    self.check_required_fields(self.service_dict, request_payload)

                hitap_service = getattr(client.service, service_name)(request_data)

            status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        finally:
            self.response.payload = {'status': status,
                                     'result': self.create_hitap_json(hitap_service)}

    def create_hitap_json(self, hitap_service):
        """Silme servisinden dönen veriyi JSON formatına döndürür.
        Converts SOAP call result object into JSON

        """
        dict_result = dict((name, getattr(hitap_service, name)) for name in dir(hitap_service)
                           if not name.startswith('__'))

        self.logger.info("hitap_service json created.")

        return dumps(dict_result)
