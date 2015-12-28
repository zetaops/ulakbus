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
    def __init__(self):
        self.service_dict = {}
        self.service_name = ''
        self.bean_name = ''
        super(HITAPService, self).__init__()

    def handle(self):
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        self.request_json(tckn, conn)

    def request_json(self, tckn, conn):
        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                hitap_service = getattr(client.service, self.service_name)(H_USER, H_PASS, tckn)
                service_bean = getattr(hitap_service, self.bean_name)

                self.logger.info("%s started to work." % (self.service_dict['service']))

                hitap_dict = self.create_hitap_dict(service_bean)

                if 'date_filter' in self.service_dict:
                    self.check_filter(hitap_dict)
                self.custom_filter(hitap_dict)

            response_json = dumps(hitap_dict)
            self.response.payload = {"status": "ok", "result": response_json}

        except AttributeError:
            self.response.payload["status"] = "error"
            self.response.payload["result"] = "TCKN may be wrong!"
            self.logger.info("TCKN may be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")

    def create_hitap_dict(self, service_bean):
        # matching fields and HITAP service values
        hitap_dict = []

        for record in service_bean:
            hitap_dict.append({
                k: getattr(record, v) for k, v in iteritems(self.service_dict['fields'])
                })

        self.logger.info("hitap_dict created.")
        return hitap_dict

    def date_filter(self, hitap_dict):
        date_filter_fields = self.service_dict['date_filter_fields']

        for field in date_filter_fields:
            hitap_dict[field] = '01.01.1900' if hitap_dict[field] == "01.01.0001" else hitap_dict[field]

    def custom_filter(self, hitap_dict):
        pass
