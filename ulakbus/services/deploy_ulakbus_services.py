# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from zato.server.service import Service
from ulakbus.models.zato import ZatoServiceChannel, ZatoServiceFile


class ServiceManagement(Service):

    @staticmethod
    def get_name():
        return "Service Management"

    def handle(self):
        ulakbus_service_files = ZatoServiceFile.objects.filter(deploy=False)
        if ulakbus_service_files:
            for ulakbus_service_file in ulakbus_service_files:

                self.invoke(
                        'zato.service.upload-package',
                        payload={"cluster_id": ulakbus_service_file.cluster_id,
                                 "payload_name": ulakbus_service_file.service_payload_name,
                                 "payload": ulakbus_service_file.service_payload})
                ulakbus_service_file.deploy = True
                ulakbus_service_file.save()
                time.sleep(0.3)

        ulakbus_channels = ZatoServiceChannel.objects.filter(deploy=False)

        if ulakbus_channels:
            for ulakbus_channel in ulakbus_channels:
                resp_service_name = self.invoke('zato.service.get-by-name',
                                                payload={
                                                    "cluster_id": 1,
                                                    "name": ulakbus_channel.service_name})
                time.sleep(0.3)
                ulakbus_channel.service_id = resp_service_name['zato_service_get_by_name_response']['id']

                resp_channel = self.invoke(
                    'zato.http-soap.create',
                    payload={"cluster_id": ulakbus_channel.cluster_id,
                             "name": ulakbus_channel.channel_name,
                             "is_active": ulakbus_channel.channel_is_active,
                             "connection": ulakbus_channel.channel_connection,
                             "transport": ulakbus_channel.channel_transport,
                             "is_internal": ulakbus_channel.channel_is_internal,
                             "url_path": ulakbus_channel.channel_url_path,
                             "data_format": ulakbus_channel.channel_data_format,
                             "service": ulakbus_channel.service_name})
                ulakbus_channel.channel_id = resp_channel['zato_http_soap_create_response']['id']

                ulakbus_channel.deploy = True
                ulakbus_channel.save()
                time.sleep(0.3)
