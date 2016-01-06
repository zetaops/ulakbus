# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zato.server.service import Service
import os
import urllib2
from json import dumps
from six import iteritems

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPService(Service):
    """
    HITAP Zato Servisi
    """

    def __init__(self):
        """
        :param service_name: HITAP servisi adi
        :type service_name: str

        :param bean_name: HITAP servisi bean adi
        :type bean_name: str

        :param service_dict: HITAP servisinden gelen veriler icin sozluk. Servisten gelen alanlarla
        modeldeki alanlarin eslendigi sozlugu ve tarih filtresi uygulanacak alanlarin listesini icerir.
        :type service_dict: dict
        """

        self.service_name = ''
        self.bean_name = ''
        self.service_dict = {}
        super(HITAPService, self).__init__()

    def handle(self):
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        self.request_json(tckn, conn)

    def request_json(self, tckn, conn):
        """
        :param tckn: Turkiye Cumhuriyeti Kimlik Numarasi
        :param conn: HITAP connection with soap

        :return: Servisten gelen verileri iceren JSON nesnesi
        """

        try:
            # soap client ile HITAP a baglanma
            with conn.client() as client:
                hitap_service = getattr(client.service, self.service_name)(H_USER, H_PASS, tckn)
                service_bean = getattr(hitap_service, self.bean_name)

                self.logger.info("%s started to work." % self.service_name)

                hitap_dict = self.create_hitap_dict(service_bean, self.service_dict['fields'])

                # veri bicimi duzenlenmesi gereken alanlara filtre uygulanmasi
                if 'date_filter' in self.service_dict:
                    self.date_filter(hitap_dict)
                self.custom_filter(hitap_dict)

            response_json = dumps(hitap_dict)
            self.response.payload = {"status": "ok", "result": response_json}

        except AttributeError as e:
            self.logger.info("AttributeError: %s" % e)
            self.response.payload["status"] = "error"
            self.response.payload["result"] = "TCKN may be wrong!"
            self.logger.info("TCKN may be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")

    def create_hitap_dict(self, service_bean, fields):
        """
        Modeldeki alanlarla HITAP servisinden donen verilerin eslenmesi

        :param service_bean: HITAP servis bean
        :param fields: Modeldeki alanlarin HITAP taki karsiliklarini tutan map

        :return: HITAP verisini modeldeki alanlara uygun bicimde tutan sozluk
        """

        hitap_dict = [{k: getattr(record, v) for k, v in iteritems(fields)} for record in service_bean]

        self.logger.info("hitap_dict created.")
        return hitap_dict

    def date_filter(self, hitap_dict):
        """
        Sozlukteki (hitap_dict) tarih alanlarinin uygun bicime getirilmesi

        :param hitap_dict: HITAP verisini modeldeki alanlara uygun bicimde tutan sozluk
        :return: hitap_dict in tarih alanlarinin uygun bicimde guncellenmis surumu
        """

        for record in hitap_dict:
            for field in self.service_dict['date_filter']:
                record[field] = '01.01.1900' if record[field] == "01.01.0001" else record[field]

    def custom_filter(self, hitap_dict):
        """
        Sozluge (hitap_dict) uygulanacak ek bicimlendirmelerin gerceklestirimi
        """
        pass
