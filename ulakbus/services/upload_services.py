# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service


class UploadServices(Service):
    name = "upload.services"

    class SimpleIO:
        input_required = ('cluster_id', 'payload_name', 'payload')

    def handle(self):
        self.invoke('zato.service.upload-package',
                    payload={"cluster_id": self.request.input['cluster_id'],
                             "payload_name": self.request.input['payload_name'],
                             "payload": self.request.input['payload']})
