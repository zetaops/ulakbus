# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zato.server.service import Service
from zato.common import DATA_FORMAT
import os
import urllib2
import socket
from json import loads, dumps
from six import iteritems


H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPSync(Service):
    """
    HITAP Synchronisation Zato Servisi

    sync field su degerlerde bulunabilir:
        1: all is good
        2: updated locally, will be updated on hitap
        3: deleted locally, will be deleted from hitap
        4: created locally, will be sent to hitap
    """

    def __init__(self):
        """
        :param sorgula_service: HITAP servisi adi
        :type sorgula_service: str

        :param model: HITAP verisinin model karsiligi
        :type model: Model
        """

        self.sorgula_service = ''
        self.model = None
        super(HITAPSync, self).__init__()

    def handle(self):
        self.logger.info("zato service started to work.")
        tckn = self.request.payload['tckn']

        self.sync_hitap_data(tckn)

    def get_hitap_dict(self, tckn):
        """
        Ilgili servise ait HITAP verisinin getirilmesi

        :param tckn: Turkiye Cumhuriyeti Kimlik Numarasi
        :return: HITAP servisinden gelen verileri iceren JSON nesnesi
        """

        response = self.invoke(self.sorgula_service, dumps({'tckn': tckn}), data_format=DATA_FORMAT.JSON, as_bunch=True)
        status = response["status"]

        hitap_dict = loads(response["result"]) if status == 'ok' else []

        return hitap_dict

    def save_hitap_data_db(self, hitap_data):
        """
        HITAP servisinden gelen verinin veritabanina kaydedilmesi

        :param hitap_data: HITAP verisinin model alanlarina uygun sekli
        :type hitap_data: dict
        """

        obj = self.model()
        for hk, hv in iteritems(hitap_data):
            setattr(obj, hk, hv)

        obj.sync = 1
        obj.save()
        self.logger.info("hitaptan gelen kayit yerelde yok, kaydedildi. kayit no => " + str(obj.kayit_no))

    def delete_hitap_data_db(self, kayit_no):
        """
        HITAP'ta olmayan verinin veritabanindan silinmesi

        :param kayit_no: HITAP verisinin kayit numarasi
        :type kayit_no: str
        """

        obj = self.model.objects.get(kayit_no=kayit_no)

        if obj.sync == 1:
            obj.delete()
            self.logger.info("yereldeki sync data, hitapta yok, kayit no degismis olabilir, kayit silindi."
                             "kayit no => " + str(obj.kayit_no))

    def sync_hitap_data(self, tckn):
        """
        HITAP servisinden gelen kayitlarin yereldeki kayitlarla senkronize edilmesi su durumlara gore gerceklesir:

        - Servisten gelen kayit veritabaninda yoksa kaydedilir.
        - Veritabaninda olup senkronize olarak gozuken kayitlar HITAP'ta yoksa, veritabanindan da silinir.

        :param tckn: Turkiye Cumhuriyeti Kimlik Numarasi
        :type tckn: str
        """

        # get hitap data
        hitap_dict = self.get_hitap_dict(tckn)

        try:
            # get kayit no list from db
            kayit_no_list = [record.kayit_no for record in self.model.objects.filter(tckn=tckn)]
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

            # if there are still some in sync records which are not in hitap data, delete them.
            for model_kayit_no in kayit_no_list:
                self.delete_hitap_data_db(model_kayit_no)

        # check for more exception
        except socket.error:
            self.logger.info("Riak connection refused!")
        except AttributeError as e:
            self.logger.info("AttributeError: %s" % e)
        except urllib2.URLError:
            self.logger.info("No internet connection!")
