# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from zato.server.service import Service
import urllib2
import json


class GetIPAddress(Service):
    """
    Informative service for development purpose
    Returns IP address of zato server's public interface
    """

    def handle(self):
        service = self.outgoing.plain_http.get('IPIFY')
        response = service.conn.get(self.cid)
        self.response.payload = {"status": "ok", "result": json.dumps(response.data)}
