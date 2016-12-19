# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
from ulakbus.services.personel.hitap.hitap_helper import HitapHelper
import os
import urllib2
from json import dumps
from six import iteritems

"""HITAP Sorgu Servisi

Hitap sorgulama servislerinin kalıtılacağı
abstract HITAP Sorgula servisini içeren modül.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi


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

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPSorgula(UlakbusService):
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

    def __init__(self):
        self.service_name = ''
        self.bean_name = ''
        self.service_dict = {}
        super(HITAPSorgula, self).__init__()

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Servise gelen istekten kimlik numarası (tckn) bilgisini alır ve
        soap outgoing bağlantısını oluşturur. Bu bilgilerle
        Hitap'a gidecek isteği hazırlayacak ve gelen cevabı elde edecek olan
        request_json fonksiyonunu çağırır.

        """

        self.logger.info("zato service started to work.")
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        self.request_json(tckn, conn)

    def request_json(self, tckn, conn):
        """
        Kimlik numarası ve kullanıcı bilgileriyle birlikte Hitap'ın ilgili servisine
        istekte bulunup gelen cevabı uygun şekilde elde eder.

        Hitap'tan gelen verilerin sisteme uygun şekilde elde edilmesi için, gerekli
        Hitap sözlüğünü yaratan ve tarih alanı gibi belli alanlara uygun filteleri
        uygulayacak olan fonksiyonları çağırır.

        Veriler uygun şekilde elde edildikten sonra servis cevabı (payload) oluşturulur.

        Args:
            tckn (str): Türkiye Cumhuriyeti Kimlik Numarası
            conn (zato.outgoing.soap.conn): Zato soap outgoing bağlantısı

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.

        """

        status = "error"
        hitap_dict = []

        try:
            # connection for hitap
            with conn.client() as client:

                if 'required_fields' in self.service_dict:
                    required_field_check = HitapHelper()
                    required_field_check.check_required_data(self.service_dict)

                # hitap response
                hitap_service = getattr(client.service, self.service_name)(H_USER, H_PASS, tckn)
                # get bean object
                service_bean = getattr(hitap_service, self.bean_name)

                self.logger.info("%s started to work." % self.service_name)
                hitap_dict = self.create_hitap_dict(service_bean, self.service_dict['fields'])

                # filtering for some fields
                if 'date_filter' in self.service_dict:
                    self.date_filter(hitap_dict)
                self.custom_filter(hitap_dict)

            status = "ok"

        except AttributeError:
            self.logger.exception("AttributeError")
            status = "error"

        except urllib2.URLError:
            self.logger.exception("Service unavailable!")
            status = "error"

        finally:
            self.response.payload = {'status': status, 'result': dumps(hitap_dict)}


    def create_hitap_dict(self, service_bean, fields):
        """
        Modeldeki alanlarla Hitap servisinden dönen verileri eşler.

        Modeldeki kayıtlarla Hitap servisindeki kayıtların alanlarının isimleri
        bir sözlük ile eşleştirilir. Böylece Hitap'tan gelen veriler
        sisteme uygun şekilde elde edilebilmektedir.

        Args:
            service_bean (obj): Hitap bean nesnesi
            fields (dict): Modeldeki alanların Hitap'taki karşılıklarını tutan map

        Returns:
            List[dict]: Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        hitap_dict = [{k: getattr(record, v) for k, v in iteritems(fields)}
                      for record in service_bean]

        self.logger.info("hitap_dict created.")
        return hitap_dict

    def date_filter(self, hitap_dict):
        """
        Hitap sözlüğündeki tarih alanlarını yerele uygun biçime getirir.

        Hitap'ta tarih alanları için ``01.01.0001`` değeri boş değer anlamına gelirken,
        yerelde ``01.01.1900`` şeklindedir.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """

        for record in hitap_dict:
            for field in self.service_dict['date_filter']:
                record[field] = '01.01.1900' if record[field] == "01.01.0001" else record[field]

    def custom_filter(self, hitap_dict):
        """
        Hitap sözlüğüne uygulanacak ek filtreleri (varsa) gerçekleştirir.

        Gerçekleştirimi bu servisten kalıtılan servislerde yapılmaktadır.

        Args:
            hitap_dict (List[dict]): Hitap verisini yerele uygun biçimde tutan sözlük listesi

        """
        pass
