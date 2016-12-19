# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

import json
from ulakbus.services.ulakbus_service import UlakbusService


class GetIPAddress(UlakbusService):
    """
    Informative service for development purpose
    Returns IP address of zato server's public interface
    """

    HAS_CHANNEL = True

    def handle(self):
        service = self.outgoing.plain_http.get('IPIFY')
        response = service.conn.get(self.cid)
        self.response.payload = {"status": "ok", "result": json.dumps(response.data)}
