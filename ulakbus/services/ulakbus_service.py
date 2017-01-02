# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zato.server.service import Service
from pyoko.lib.utils import un_camel


class UlakbusService(Service):

    @classmethod
    def get_name(cls):
        return un_camel(cls.__name__, dash='-')

    @staticmethod
    def check_required_fields(service_dict, request_payload):
        """Gelen ``service_dict` içindeki ``required_fields`` sözlük listesi içinde belirtilen servis
        tarafında servis tarafında gerekli olarak tanımlanmış alanların hem ``fields`` sözlüğü
        içinde tanımlı olup olmadığını hem de bu alanların değerinin null olmadığını kontrol
        eder.

        Args:
            service_dict (dict) : HITAP servisine gönderilmek üzere hazırlanmış sözlük listesi.

        """
        for required_field in service_dict['required_fields']:
            try:
                if not request_payload[service_dict['fields'][required_field]]:
                    raise ValueError("required %s field's value is null" % required_field)
            except KeyError:
                raise KeyError("required field %s not found in hitap service dict" % required_field)
