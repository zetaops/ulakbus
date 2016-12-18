# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field
from zengine.lib.translation import gettext_lazy as __


class ZatoServiceFile(Model):

    cluster_id = field.Integer(__(u'Zato cluster'))
    service_payload_name = field.String(__(u"Module’s file name"))
    service_payload = field.String(__(u"BASE64-encoded"))
    deploy = field.Boolean(__(u"Deploy Service"), default=False)

    def __unicode__(self):
        return self.service_payload_name


class ZatoServiceChannel(Model):
    cluster_id = field.Integer(__(u'Zato cluster'))
    channel_id = field.Integer(__(u"Channel id"))
    channel_name = field.String(__(u"Channel name"))
    channel_connection = field.String(__(u"channel or outgoing connection"))
    channel_transport = field.String(__(u"plain_http or soap"))
    channel_url_path = field.String(__(u"Example: /test/zato-url-path"))
    channel_data_format = field.String(__(u"xml or json"))
    channel_is_internal = field.Boolean(default=False)
    channel_is_active = field.Boolean(default=True)
    service_id = field.Integer(__(u"Service Id"))
    service_name = field.String(__(u"Service name"))
    deploy = field.Boolean(__(u"Deploy Channel"), default=False)

    def __unicode__(self):
        return self.channel_name
