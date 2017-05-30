# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import urllib2

from ulakbus.services.personel.hitap.hitap_service import ZatoHitapService
from json import dumps

"""HITAP Sorgu Servisi

Hitap sorgulama servislerinin kalıtılacağı
abstract HITAP Sorgula servisini içeren modül.

Example:
    Servise JSON nesnesi kullanılarak istek gönderilmesi:

    .. code-block:: json

        $ curl http://localhost:11223/hizmet-okul-getir -d '{"tckn": "tckn"}'


    İsteğe dönen cevap:

    .. code-block:: json

        $ {
            'status': 'ok',
            'result': '[{
                "hazirlik": 0,
                "ogrenim_yeri": "1",
                "mezuniyet_tarihi": "07.12.2005",
                "denklik_okul": null,
                "denklik_bolum": null,
                "tckn": "tckn",
                "ogrenim_durumu": 7,
                "kayit_no": 1234567,
                "kurum_onay_tarihi": null,
                "okul_ad": "YENI MAHALLE LİSESİ",
                "bolum": "SOSYAL BİLİMLER",
                "denklik_tarihi": "01.01.1900",
                "ogrenim_suresi": 4
                },
                ...
            }]'
        }

"""


class HITAPSorgula(ZatoHitapService):
    """
    Hitap Sorgulama servislerinin kalıtılacağı abstract Zato servisi.

    Sorgulama servisleri gerekli girdileri (Hitap username, Hitap password, tckn)
    Hitap'a yollayıp dönecek cevabı elde edebilmektedirler.

    Attributes:
        service_name (str): İlgili Hitap sorgu servisinin adı
        bean_name (str): Hitap'tan gelen bean nesnesinin adı
        service_dict (dict): Hitap servisinden gelen cevap için sözlük.
            Cevabın içerdiği alanlarla modeldeki alanların eşlendiği sözlüğü
            ve tarih filtresi uygulanacak alanların listesini içerir.

    """
    HAS_CHANNEL = False

    def request_json(self, conn, request_payload):
        """
        Kimlik numarası ve kullanıcı bilgileriyle birlikte Hitap'ın ilgili servisine
        istekte bulunup gelen cevabı uygun şekilde elde eder.

        Hitap'tan gelen verilerin sisteme uygun şekilde elde edilmesi için, gerekli
        Hitap sözlüğünü yaratan ve tarih alanı gibi belli alanlara uygun filteleri
        uygulayacak olan fonksiyonları çağırır.

        Veriler uygun şekilde elde edildikten sonra servis cevabı (payload) oluşturulur.

        Args:
            request_payload (str): Türkiye Cumhuriyeti Kimlik Numarası
            conn (zato.outgoing.soap.conn): Zato soap outgoing bağlantısı

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.

        """

        status = "error"
        hitap_dicts = []
        service_name = self.service_dict['service_name']
        bean_name = self.service_dict['bean_name']
        try:
            # connection for hitap
            with conn.client() as client:

                if 'required_fields' in self.service_dict:
                    self.check_required_fields(request_payload)

                # hitap response
                self.logger.info("SORGULA SERVIS NAME : %s" % service_name)
                hitap_service = getattr(client.service,
                                        service_name)(request_payload['kullanici_ad'],
                                                      request_payload['kullanici_sifre'],
                                                      request_payload['tckn'])
                # get bean object
                service_beans = getattr(hitap_service, bean_name)

                self.logger.info("%s started to work." % service_name)

                hitap_dicts = self.hitap_json(service_beans)

                # filtering for some fields
                if 'date_filter' in self.service_dict:
                    self.logger.info("Hitap dict: %s" % hitap_dicts)
                    for hitap_dict in hitap_dicts:
                        self.date_filter_hitap_to_ulakbus(self.service_dict['date_filter'],
                                                          hitap_dict)
                if 'long_to_string' in self.service_dict:
                    for hitap_dict in hitap_dicts:
                        self.long_to_string(hitap_dict)

            status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        finally:
            self.response.payload = {'status': status, 'result': dumps(hitap_dicts)}

    def hitap_json(self, data):
        data_dicts = [{k: getattr(record, v) for k, v in self.service_dict['fields'].items()}
                      for record in data]
        return data_dicts

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri (varsa) gerçekleştirir.

        Gerçekleştirimi bu servisten kalıtılan servislerde yapılmaktadır.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        pass
