# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service


class CreateServiceChannel(Service):
    name = "create.service.channel"

    class SimpleIO:
        input_required = ('cluster_id', 'name', 'is_active', 'connection', 'transport',
                          'is_internal', 'url_path', 'data_format', 'service')

    def handle(self):
        self.invoke('zato.http-soap.create',
                    payload={"cluster_id": self.request.input['cluster_id'],
                             "name": self.request.input['name'],
                             "is_active": self.request.input['is_active'],
                             "connection": self.request.input['connection'],
                             "transport": self.request.input['transport'],
                             "is_internal": self.request.input['is_internal'],
                             "url_path": self.request.input['url_path'],
                             "data_format": self.request.input['data_format'],
                             "service": self.request.input['service']})
