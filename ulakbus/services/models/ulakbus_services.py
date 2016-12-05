# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field


class UlakbusService(Model):

    cluster_id = field.Integer('Zato cluster')
    service_id = field.Integer("Service id")
    service_name = field.String("Service name")
    service_payload_name = field.String("Module’s file name")
    service_payload = field.String("BASE64-encoded")
    channel_id = field.Integer("Channel id")
    channel_name = field.String("Channel name")
    channel_connection = field.String("channel or outgoing connection")
    channel_transport = field.String("plain_http or soap")
    channel_url_path = field.String("Example: /test/zato-url-path")
    channel_data_format = field.String("xml or json")
    channel_is_internal = field.Boolean(default=False)
    channel_is_active = field.Boolean(default=True)
    deploy = field.Boolean("Deploy service")

    def __unicode__(self):
        return self.service_name
