# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import ZatoHitapService
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


class HITAPGuncelle(ZatoHitapService):
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

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.

        """

        status = "error"
        hitap_service = {}
        service_name = self.service_dict['service_name']
        try:
            # connection for hitap
            with conn.client() as client:
                # hitap response
                service_call_name = self.service_dict["service_mapper"]

                if service_call_name:
                    request_data = client.factory.create(service_call_name)

                    # filtering for some fields
                    if 'date_filter' in self.service_dict:
                        self.date_filter_ulakbus_to_hitap(self.service_dict['date_filter'],
                                                          request_payload)

                    if 'required_fields' in self.service_dict:
                        self.check_required_fields(request_payload)

                    for dict_element in self.service_dict['fields']:
                        setattr(request_data, dict_element,
                                request_payload[self.service_dict['fields'][dict_element]])

                    self.logger.info("%s started to work." % service_name)

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

        finally:
            self.response.payload = {'status': status,
                                     'result': self.create_hitap_json(hitap_service)}

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri (varsa) gerçekleştirir.

        Gerçekleştirimi bu servisten kalıtılan servislerde yapılmaktadır.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        pass
