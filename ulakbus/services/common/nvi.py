# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from zato.server.service import Service
import urllib2
import json


#
# suds example of nvi service
# from suds.wsse import *
# from suds.client import Client
# security = Security()
# wsdl = 'https://kpsbasvuru.nvi.gov.tr/Services/WsdlNoPolicy.ashx?Service=KisiSorgulaTCKimlikNoServis'
# client = Client(wsdl)
# token = UsernameToken('****', '****')
# security.tokens.append(token)
# client.set_options(wsse=security)
# result = client.service.ListeleCoklu(12345678900)
#

class KimlikBilgileriGetir(Service):
    """
    NVI Kimlik Bilgileri Servisi
    """

    def handle(self):
        tckn = self.request.payload['tckn']
        conn = self.outgoing.soap['KisiSorgulaTCKimlikNoServisNoPolicy'].conn

        # connects with soap client to the HITAP
        try:
            with conn.client() as client:
                result = client.service.ListeleCoklu(int(tckn))  # nvi requires tckn as integer
                self.logger.info("NVI service fired!..")

            self.response.payload = {"status": "ok", "result": json.dumps(result)}

        except AttributeError:
            pass
        except urllib2.URLError:
            self.logger.info("No internet connection!")
