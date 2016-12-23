# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
from ulakbus.services.personel.hitap.hitap_helper import HitapHelper
import os
import urllib2
from json import dumps

"""HITAP Guncelle Servisi

Hitap guncelle (insert) servislerinin kalıtılacağı
abstract HITAP Guncelle servisini içeren modül.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi

"""

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPGuncelle(UlakbusService):
    """
    Hitap Güncelleme servislerinin kalıtılacağı abstract Zato servisi.

    Güncelleme servisleri gerekli girdileri (Hitap dict, Hitap username, Hitap password)
    Hitap'a yollayıp dönecek cevabı elde etmektedir.

    Attributes:
        service_name (str): İlgili Hitap sorgu servisinin adı
        service_dict (dict): Hitap servisine yollanacak datayı hazırlamak için sözlük.
            Servise gönderilecek verinin alanlarına ait sözlüğü
            ve tarih filtresi uygulanacak ve servis tarafında gerekli olan alanların
            listesini içerir.

    """
    HAS_CHANNEL = False

    def __init__(self):
        self.service_name = ''
        self.service_dict = {'fields': {}, 'date_filter': [], 'required_fields': []}
        super(HITAPGuncelle, self).__init__()

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Hitap'a gidecek isteği hazırlayacak ve gelen cevabı elde edecek olan
        request_json fonksiyonunu çağırır.

        """

        self.logger.info("zato service started to work.")
        conn = self.outgoing.soap['HITAP'].conn

        self.request_json(conn)

    def request_json(self, conn):
        """
        Connection bilgisi ve gerekli veriler ile Hitap'ın ilgili servisine
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
        hitap_response = False
        request_data = {}

        try:
            # connection for hitap
            with conn.client() as client:
                # hitap response
                service_call_name = self.service_mapper(self.service_name)

                if service_call_name:
                    request_data = client.factory.create(service_call_name)

                # filtering for some fields
                if 'date_filter' in self.service_dict:
                    self.date_filter(self.service_dict)
                self.custom_filter(self.service_dict)

                if 'required_fields' in self.service_dict:
                    required_field_check = HitapHelper()
                    required_field_check.check_required_data(self.service_dict)

                for dict_element in self.service_dict['fields']:
                    request_data[dict_element] = self.service_dict[dict_element]

                self.logger.info("%s started to work." % self.service_name)

                hitap_response = getattr(client.service, self.service_name)(request_data,
                                                                            kullaniciAd=H_USER,
                                                                            sifre=H_PASS)
                if hitap_response:
                    hitap_response = self.create_hitap_json(hitap_response)

            status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        finally:
            self.response.payload = {'status': status, 'result': hitap_response}

    def create_hitap_json(self, hitap_service):
        """Güncelleme servisinden dönen veriyi JSON formatına döndürür.
        Converts SOAP call result object into JSON

        """
        dict_result = dict((name, getattr(hitap_service, name)) for name in dir(hitap_service)
                           if not name.startswith('__'))

        self.logger.info("hitap_service json created.")

        return dumps(dict_result)

    def date_filter(self, hitap_dict):
        """
        Yerel kayıttaki tarih alanlarını HITAP servisine uygun biçime getirir.

        Hitap'ta tarih alanları için ``0001-01-01`` değeri boş değer anlamına gelirken,
        yerelde ``01.01.1900`` şeklindedir.

        Yerelde GG-AA-YYYY formatında tutulurken, HITAP servisi üzerindeki geçerli format YYYY-AA-GG
        şeklindedir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        if hitap_dict['date_filter']:
            from datetime import datetime
            for record in hitap_dict:
                for field in hitap_dict['date_filter']:
                    if record[field] == "01.01.1900":
                        record[field] = '0001-01-01'
                    else:
                        date_format = datetime.strptime(record[field], "%d.%m.%Y")
                        record[field] = date_format.strftime("%Y-%m-%d")

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri (varsa) gerçekleştirir.

        Gerçekleştirimi bu servisten kalıtılan servislerde yapılmaktadır.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        pass

    def service_mapper(self, service_name):

        """Hitap'a yapılacak olan Update çağrılarında gerekli datanın oluşmasını sağlamak için
        Servis ve ServisBean'lerini eşleyen method.

        """
        services_dict = {"HizmetAcikSureUpdate": "ns1:HizmetAcikSureServisBean",
                         "HizmetAskerlikUpdate": "ns1:HizmetAskerlikServisBean",
                         "HizmetBirlestirmeUpdate": "ns1:HizmetBirlestirmeServisBean",
                         "HizmetBorclanmaUpdate": "ns1:HizmetBorclanmaServisBean",
                         "HizmetCetvelUpdate": "ns1:HizmetCetveliServisBean",
                         "HizmetIHSUpdate": "ns1:HizmetIHSServisBean",
                         "HizmetKursUpdate": "ns1:HizmetEgitimKursServisBean",
                         "HizmetMahkemeUpdate": "ns1:HizmetMahkemeServisBean",
                         "HizmetNufusUpdate": "ns1:HizmetNufusServisBean",
                         "HizmetOkulUpdate": "ns1:HizmetEgitimOkulServisBean",
                         "HizmetTazminatUpdate": "ns1:HizmetTazminatServisBean",
                         "HizmetUnvanUpdate": "ns1:HizmetUnvanServisBean",
                         "hizmetIstisnaiIlgiUpdate": "ns1:HizmetIstisnaiIlgiServisBean"}

        if service_name in services_dict:
            return services_dict[service_name]
        else:
            return False
