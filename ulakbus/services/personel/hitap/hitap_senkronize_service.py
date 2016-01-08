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


class HITAPSenkronizeService(Service):
    """
    HITAP Senkronize Zato Servisi
    """

    def __init__(self):
        """
        :param service_name: HITAP servisi adi
        :type service_name: str

        :param bean_name: HITAP servisi bean adi
        :type bean_name: str

        """

        self.service_name = ''
        self.bean_name = ''
        self.model = None
        super(HITAPSenkronizeService, self).__init__()

    def handle(self):
        self.logger.info("zato service started to work.")
        tckn = self.request.payload['tckn']

        hitap_dict = self.get_hitap_dict(tckn)
        # if it is saved before, find that and add new records from hitap to riak
        try:
            model_kayit_no_list = [record.kayit_no for record in self.model.objects.filter(tckn=tckn)]

            self.logger.info("Localdeki kayit sayisi: " + str(len(model_kayit_no_list)))
            self.logger.info("Hitaptan gelen kayit sayisi: " + str(len(hitap_dict)))

            for hitap_record in hitap_dict:
                hitap_kayit_no = hitap_record['kayit_no']

                if hitap_kayit_no in model_kayit_no_list:
                    self.logger.info("hitap gelen data localde var.")
                    obj = self.model.objects.get(kayit_no=hitap_kayit_no)

                    if obj.sync == 1:
                        self.logger.info("hitaptan gelen data localde var ve senkronize.")
                    elif obj.sync == 2:
                        for hk, hv in iteritems(hitap_record):
                            setattr(obj, hk, hv)
                        obj.sync = 1
                        obj.save()
                        self.logger.info("hitap gelen data localde senkronize edildi.")
                    else:
                        pass

                    model_kayit_no_list.remove(hitap_kayit_no)
                else:
                    self.logger.info("hitap gelen data localde yok. Kayit no => " + str(hitap_kayit_no))
                    obj = self.model()
                    for hk, hv in iteritems(hitap_record):
                        setattr(obj, hk, hv)
                    obj.sync = 1
                    obj.save()

            for model_kayit_no in model_kayit_no_list:
                obj = self.model.objects.get(kayit_no=model_kayit_no)
                if obj.sync == 1:
                    obj.delete()
                    self.logger.info("localdeki sync data, hitapta yok, kayit no degismis olabilir, kayit silindi.")
                else:
                    pass

        # If not any record belongs to given tcno, create new one
        except IndexError:
            for hitap_record in hitap_dict:
                hitap_kayit_no = hitap_record['kayit_no']
                obj = self.model()
                for hk, hv in iteritems(hitap_record):
                    setattr(obj, hk, hv)
                obj.sync = 1
                obj.save()
                self.logger.info("new record saved.")
            # sleep(1)
        except socket.error:
            self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")


    def get_hitap_dict(self, tckn):
        response = self.invoke(self.service_name, dumps({'tckn': tckn}), data_format=DATA_FORMAT.JSON, as_bunch=True)
        status = response["status"]

        hitap_dict = loads(response["result"]) if status == 'ok' else {}

        return hitap_dict