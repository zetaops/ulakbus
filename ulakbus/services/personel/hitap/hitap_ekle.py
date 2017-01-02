# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.ulakbus_service import UlakbusService
import os
import urllib2
from json import dumps

"""ITAP Ekle Servisi

Hitap ekle (insert) servislerinin kalıtılacağı
abstract HITAP Ekle servisini içeren modül.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi

"""
H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPEkle(UlakbusService):
    """
    Hitap Ekleme servislerinin kalıtılacağı abstract Zato servisi.

    Ekleme servisleri gerekli girdileri (Hitap dict, Hitap username, Hitap password)
    Hitap'a yollayıp dönecek cevabı elde edebilmektedirler.

    Attributes:
        service_name (str): İlgili Hitap sorgu servisinin adı
        service_dict (dict): Hitap servisine yollanacak datayı hazırlamak için sözlük.
            Servise gönderilecek verinin alanlarına ait sözlüğü
            ve tarih filtresi uygulanacak alanların listesini içerir.

    """
    HAS_CHANNEL = False
    service_dict = {"fields": {}, "date_filter": [], "required_fields": [], "service_name": ''}

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
        """
        Connection bilgisi ve gerekli veriler ile Hitap'ın ilgili servisine
        istekte bulunup gelen cevabı uygun şekilde elde eder.

        Hitap'tan gelen verilerin sisteme uygun şekilde elde edilmesi için, gerekli
        Hitap sözlüğünü yaratan ve tarih alanı gibi belli alanlara uygun filteleri
        uygulayacak olan fonksiyonları çağırır.

        Veriler uygun şekilde elde edildikten sonra servis cevabı (payload) oluşturulur.

        Args:
            conn (zato.outgoing.soap.conn): Zato soap outgoing bağlantısı
            request_payload: Zato servisine bagli kanala gonderilen parametreler ve degerleri.
                             Örnek: {'tckn':112343214, 'karar_no': 666 }

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.

        """

        status = "error"
        hitap_service = ""
        service_name = self.service_dict['service_name']
        try:
            # connection for hitap
            with conn.client() as client:
                # hitap response

                self.logger.info("HITAP EKLE SERVICE NAME : %s" % service_name)
                service_call_name = self.service_mapper(service_name)

                self.logger.info("Service Call Name: %s" % service_call_name)

                if service_call_name:
                    request_data = client.factory.create(service_call_name)

                    self.logger.info("Request data: %s", request_data)
                    self.logger.info("Request data TYPE: %s", type(request_data))

                    if hasattr(request_data, 'kayitNo'):
                        del request_data.kayitNo
                    elif hasattr(request_data, 'ihzID'):
                        del request_data.ihzID

                    # filtering for some fields
                    if 'date_filter' in self.service_dict:
                        self.date_filter(self.service_dict['date_filter'], request_payload)

                    if 'required_fields' in self.service_dict:
                        self.check_required_fields(self.service_dict, request_payload)

                    for dict_element in self.service_dict['fields']:
                        self.logger.info("Dict element : %s", dict_element)
                        setattr(request_data, dict_element, request_payload[self.service_dict['fields'][dict_element]])

                    self.logger.info("Request data: %s", request_data)
                    self.logger.info("HITAP EKLE SERVICE NAME: %s", service_name)
                    hitap_service = getattr(client.service, service_name)(request_data,
                                                                          kullaniciAd=H_USER,
                                                                          sifre=H_PASS)
            status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        except Exception as e:
            self.logger.exception("Bilinmeyen hata: %s" % e)
        finally:
            self.logger.info("Hitap servis: %s" % hitap_service)
            self.response.payload = {'status': status,
                                     'result': self.create_hitap_json(hitap_service)}

    def create_hitap_json(self, hitap_service):
        """Ekleme servisinden dönen veriyi JSON formatına döndürür.
        Converts SOAP call result object into JSON

        """
        dict_result = dict((name, getattr(hitap_service, name)) for name in dir(hitap_service)
                           if not name.startswith('__'))

        self.logger.info("hitap_service json created.")

        return dumps(dict_result)

    def date_filter(self, date_filter_fields, request_payload):
        """
        Yerel kayıttaki tarih alanlarını HITAP servisine uygun biçime getirir.

        Hitap'ta tarih alanları için ``0001-01-01`` değeri boş değer anlamına gelirken,
        yerelde ``01.01.1900`` şeklindedir.

        Yerelde GG-AA-YYYY formatında tutulurken, HITAP servisi üzerindeki geçerli format YYYY-AA-GG
        şeklindedir.

        Args:
            date_filter_fields (List[]): Zato servisinde bulunan ve tarih formatinda olan field isimleri listesi

        """
        from datetime import datetime
        for field in date_filter_fields:
            date_field = self.service_dict['fields'][field]
            if request_payload[date_field] == "01.01.1900":
                request_payload[date_field] = '0001-01-01'
            else:
                date_format = datetime.strptime(request_payload[date_field], "%d.%m.%Y")
                request_payload[date_field] = date_format.strftime("%Y-%m-%d")

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri (varsa) gerçekleştirir.

        Gerçekleştirimi bu servisten kalıtılan servislerde yapılmaktadır.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        pass

    def service_mapper(self, service_name):

        """Hitap'a yapılacak olan Ekleme çağrılarında gerekli datanın oluşmasını sağlamak için
        Servis ve ServisBean'lerini eşleyen method.

        """
        services_dict = {"HizmetAcikSureInsert": "ns1:HizmetAcikSureServisBean",
                         "HizmetAskerlikInsert": "ns1:HizmetAskerlikServisBean",
                         "HizmetBirlestirmeInsert": "ns1:HizmetBirlestirmeServisBean",
                         "HizmetBorclanmaInsert": "ns1:HizmetBorclanmaServisBean",
                         "HizmetCetvelInsert": "ns1:HizmetCetveliServisBean",
                         "HizmetIHSInsert": "ns1:HizmetIHSServisBean",
                         "HizmetKursInsert": "ns1:HizmetEgitimKursServisBean",
                         "HizmetMahkemeInsert": "ns1:HizmetMahkemeServisBean",
                         "HizmetNufusInsert": "ns1:HizmetNufusServisBean",
                         "HizmetOkulInsert": "ns1:HizmetEgitimOkulServisBean",
                         "HizmetTazminatInsert": "ns1:HizmetTazminatServisBean",
                         "HizmetUnvanInsert": "ns1:HizmetUnvanServisBean",
                         "hizmetIstisnaiIlgiInsert": "ns1:HizmetIstisnaiIlgiServisBean"}

        if service_name in services_dict:
            return services_dict[service_name]
        else:
            return False
