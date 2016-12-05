# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
from ulakbus.services.models.ulakbus_services import UlakbusService
import time


class ServiceManagement(Service):

    @staticmethod
    def get_name():
        return "Service Management"

    def handle(self):
        ulakbus_services = UlakbusService.objects.filter(deploy=True)
        if ulakbus_services:
            for ulakbus_service in ulakbus_services:
                self.invoke(
                    'zato.service.upload-package',
                    payload={"cluster_id": ulakbus_service.cluster_id,
                             "payload_name": ulakbus_service.service_payload_name,
                             "payload": ulakbus_service.service_payload})

                time.sleep(0.3)

                resp_service = self.invoke('zato.service.get-by-name',
                                           payload={
                                               "cluster_id": ulakbus_service.cluster_id,
                                               "name": ulakbus_service.service_name})

                ulakbus_service.service_id = resp_service['zato_service_get_by_name_response']['id']

                time.sleep(0.3)

                resp_channel = self.invoke(
                    'zato.http-soap.create',
                    payload={"cluster_id": ulakbus_service.cluster_id,
                             "name": ulakbus_service.channel_name,
                             "is_active": ulakbus_service.channel_is_active,
                             "connection": ulakbus_service.channel_connection,
                             "transport": ulakbus_service.channel_transport,
                             "is_internal": ulakbus_service.channel_is_internal,
                             "url_path": ulakbus_service.channel_url_path,
                             "data_format": ulakbus_service.channel_data_format,
                             "service": ulakbus_service.service_name})
                ulakbus_service.channel_id = resp_channel['zato_http_soaxp_create_response']['id']

                ulakbus_service.deploy = False
                ulakbus_service.save()

        else:
            self.response.payload = {"Info :": "Tum servisler guncel..."}
