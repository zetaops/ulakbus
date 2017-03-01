# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.services.ulakbus_service import ZatoHitapService
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


class HITAPEkle(ZatoHitapService):
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
                service_call_name = self.service_dict["service_mapper"]

                self.logger.info("Service Call Name: %s" % service_call_name)

                if service_call_name:
                    request_data = client.factory.create(service_call_name)

                    self.logger.info("Request data: %s", request_data)
                    self.logger.info("Request payload: %s", request_payload)

                    # filtering for some fields
                    if 'date_filter' in self.service_dict:
                        self.date_filter_ulakbus_to_hitap(self.service_dict['date_filter'],
                                                          request_payload)

                    if 'required_fields' in self.service_dict:
                        self.check_required_fields(request_payload)

                    for dict_element in self.service_dict['fields']:
                        self.logger.info("Dict element : %s", dict_element)
                        setattr(request_data, dict_element,
                                request_payload[self.service_dict['fields'][dict_element]])

                    self.logger.info("Request data: %s", request_data)
                    self.logger.info("HITAP EKLE SERVICE NAME: %s", service_name)
                    hitap_service = getattr(client.service, service_name)(request_data,
                                                                          kullaniciAd=H_USER,
                                                                          sifre=H_PASS)
                    self.logger.info("Hitap Service: %s" % hitap_service)
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
