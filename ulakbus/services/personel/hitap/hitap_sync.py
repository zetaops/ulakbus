# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
from zato.common import DATA_FORMAT
import os
import urllib2
import socket
from json import loads, dumps
from six import iteritems
from ulakbus.models.personel import Personel

"""HITAP Senkronizasyon Servisi

Hitap senkronizasyon servislerinin kalıtılacağı
abstract HITAP Sorgula servisini içeren modül.

Bu servis şu işlemleri gerçekleştirir:

    * Hitap'taki kayıt yerelde yoksa, yerele kaydedilir.
    * Yereldeki kayıt Hitap'ta yoksa ve sync değeri 1 (senkronize) görünüyorsa,
      Hitap'ta bu kayıt silinmiş demektir ve yerelde de silinir.

``sync`` alanı şu değerlerde bulunabilir:

    * 1: Kayıt Hitap ile senkronize
    * 2: Yerel kayıt güncellendi, Hitap güncellenecek
    * 3: Yerel kayıt silindi, Hitap kaydı silinecek
    * 4: Yeni bir yerel kayıt oluşturuldu, Hitap'a gönderilecek.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi


Example:
    Servise JSON nesnesi kullanılarak istek gönderilmesi:

    .. code-block:: json

        $ curl http://localhost:11223/hizmet-okul-sync -d '{"tckn": "tckn"}'

"""

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPSync(UlakbusService):
    """
    Hitap Sync servislerinin kalıtılacağı abstract Zato servisi.

    Senkronizasyon servisleri gerekli girdileri (Hitap username, Hitap password, tckn)
    Hitap sorgulama servislerine gönderip dönecek cevaba göre
    yereldeki kayıtları güncelleyebilmektedirler.

    Attributes:
        sorgula_service (str): İlgili Hitap sorgu servisinin adı
        model (Model): Hitap'taki kaydın karşılığı olan Model

    """
    HAS_CHANNEL = False

    def __init__(self):
        self.sorgula_service = ''
        self.model = None
        super(HITAPSync, self).__init__()

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Servise gelen istekten kimlik numarası (tckn) bilgisini alır ve
        Hitap sorgulama servisine gidecek isteği hazırlayacak
        ve gelen cevabı elde edecek olan sync_hitap_data fonksiyonunu çağırır.

        """

        self.logger.info("zato service started to work.")
        tckn = self.request.payload['tckn']
        self.personel = Personel.objects.filter(tckn=tckn)[0]

        self.sync_hitap_data(tckn)

    def get_hitap_dict(self, tckn):
        """
        İlgili servise ait sorgulama servisini çağırarak
        gerekli Hitap verisini elde eder.

        Args:
            tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

        Returns:
            (List[dict], Bool):
                Hitap verisini yerele uygun biçimde tutan sözlük listesi ve
                Sorgu sonucunda hata olup olmadığı bilgisi

        """

        response = self.invoke(self.sorgula_service, dumps({'tckn': tckn}),
                               data_format=DATA_FORMAT.JSON, as_bunch=True)

        has_error = True if response["status"] == 'error' else False
        hitap_dict = loads(response["result"])

        return hitap_dict, has_error

    def save_hitap_data_db(self, hitap_data):
        """
        Hitap servisinden gelen kayıt yerelde yoksa, sync değeri 1 (senkronize)
        olacak şekilde kaydı veritabanına kaydeder.

        Args:
            hitap_data (dict): Hitap verisini yerele uygun biçimde tutan sözlük

        """

        obj = self.model()
        for hk, hv in iteritems(hitap_data):
            setattr(obj, hk, hv)

        obj.sync = 1
        obj.personel = self.personel
        obj.save()
        self.logger.info("hitaptaki kayit yerele kaydedildi. kayit no => "
                         + str(obj.kayit_no))

    def delete_hitap_data_db(self, kayit_no):
        """
        Yereldeki kayıt Hitap'ta yoksa ve sync değeri 1 (senkronize) görünüyorsa,
        Hitap'ta bu kayıt silinmiş demektir ve yerelde de silinir.

        Args:
            kayit_no (str): Hitap kaydının kayıt numarası

        """

        obj = self.model.objects.get(kayit_no=kayit_no)

        if obj.sync == 1:
            obj.delete()
            self.logger.info("yereldeki sync kayit hitapta yok, kayit silindi."
                             "kayit no => " + str(obj.kayit_no))

    def sync_hitap_data(self, tckn):
        """
        Yereldeki kayıtları Hitap servisinden gelen kayıtlara göre senkronize eder.
        tckn bilgisine göre Hitap kayıtları ve yereldeki kayıtları getirilir ve:

            * Hitap'taki kayıt yerelde yoksa, yerele kaydedilir.
            * Yereldeki kayıt Hitap'ta yoksa ve sync değeri 1 (senkronize) görünüyorsa,
              Hitap'ta bu kayıt silinmiş demektir ve yerelde de silinir.

        Args:
            tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

        Raises:
            AttributeError: İlgili servis veya bean Hitap'ta bulunmayabilir.
            urllib2.URLError: Servis yanıt vermiyor.
            socket.error: Riak bağlantı hatası.
            Exception: Beklenmeyen hata.

        """

        # get hitap data
        hitap_dict, has_error = self.get_hitap_dict(tckn)

        if has_error:
            self.logger.info("Hitap kaydi sorgulama hatasi.")
            status = "error"
            result = "Service unavailable!"
        else:
            try:
                # get kayit no list from db
                kayit_no_list = [record.kayit_no for record in
                                 self.model.objects.filter(tckn=tckn)]
                self.logger.info("yereldeki kayit sayisi: " + str(len(kayit_no_list)))
                self.logger.info("hitaptan gelen kayit sayisi: " + str(len(hitap_dict)))

                # compare hitap data with db
                for hitap_record in hitap_dict:
                    hitap_kayit_no = hitap_record['kayit_no']

                    # if hitap data is not in db, create an object and save to db.
                    if hitap_kayit_no not in kayit_no_list:
                        self.save_hitap_data_db(hitap_record)
                    # if in db, don't touch.
                    else:
                        kayit_no_list.remove(hitap_kayit_no)

                # if there are still some in sync records which are not in hitap, delete them.
                for model_kayit_no in kayit_no_list:
                    self.delete_hitap_data_db(model_kayit_no)

                status = "ok"
                result = "Synchronisation completed successfully."

            except AttributeError:
                self.logger.exception("AttributeError")
                status = "error"
                result = "AttributeError"
            except socket.error:
                self.logger.exception("Riak connection refused!")
                status = "error"
                result = "Riak connection refused!"
            except urllib2.URLError:
                self.logger.exception("Service unavailable!")
                status = "error"
                result = "Service unavailable!"
            except Exception:
                self.logger.exception("Unexpected error!")
                status = "error"
                result = "Unexpected error!"

        self.logger.info(result)
        self.response.payload = {'status': status, 'result': result}
