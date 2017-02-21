# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Zato Service Wrapper

Includes Zato Service Wrapper and wrapper functions for services
such as Hitap, Mernis, KPS etc.


Example:

    .. code-block:: python

        zs = HitapService(service_name='hizmet-cetveli-sil', payload="{'tckn': 121231,
                                                                       'kayit_no': 234}")
        response = zs.zato_request()  # 'ok' or 'error'
        zs = HitapHizmetCetvelGetir(tckn="12345678900")
        response = zs.zato_request()  # list, with lines of hizmet cetveli


    .. code-block:: python

        from zato_wrapper_class import ZatoService
        zs = ZatoService(service_name='kisi-sorgula-tc-kimlik-no', payload="12312342131")
        response = zs.zato_request()  # 'ok' or 'error'

"""

from pyoko.conf import settings
import requests
import json
import urlparse
import importlib
from ulakbus.models import ZatoServiceChannel


class ZatoService(object):
    """
    Simple zato service wrapper class.
    You can write your zato services extending this class.

    This class simply needs some parameter to be set
    as you see in init payload and service uri.

    Ping service returns just 'ok' which can be used as an health check
    to determine zato servers is alive or not.

    ``service_uri`` and ``payload`` parameters especially is
    set by extending class' __init__.

    """

    def __init__(self, service_name, payload):
        self.zato_service = ZatoServiceChannel.objects.get(service_name=service_name)
        self.payload = payload

    def prepare_payload(self):
        return self.payload

    def get_uri(self):
        """
        Simply returns full uri of zato service object.
        It uses ``ZATO_SERVER`` from settings module.

        The ``ZATO_SERVER`` can be set as environment variable as below::

            export ZATO_SERVER='http://127.0.0.1/'

        Returns:
            (str): unique identification string of service on zato services
            including join of zato server url (generally a load balancer url)
            and service name on zato.

        """

        return urlparse.urljoin(settings.ZATO_SERVER, self.zato_service.channel_url_path)

    def zato_request(self):
        """
        Makes zato requests. Zato expects payloads as json over POST method
        and sends back json. Return json contains two parts
        one is status and the other is result.

        Status part is can be ``ok`` or ``error`` depends on
        what happens in zato servers while running. Result part is
        the data part which is expected by consumer.

        Returns:
            str: if requests fails, returns ``None``
            or simply string of zato service response payload

        """
        r = requests.post(self.get_uri(), data=json.dumps(self.prepare_payload()))
        if r.status_code == 200:
            response = r.json()
            r.close()
            try:
                if response['status'] == 'ok':
                    return self.rebuild_response(response)
                else:
                    # all zato internal errors will be handled here,
                    # riak error, connection error etc..
                    raise Exception("your service request failed with error %s"
                                    % response['result'])
            except KeyError:
                raise Exception("your service response contains no status code, "
                                "check your zato service package")

        if r.status_code == 404:
            raise Exception("Service called '%s' is not defined on zato "
                            "servers or service_uri changed" % self.zato_service.channel_url_path)
        # other than 404 errors will be handled here,
        # such as unauthorized requests, permission denied or etc..
        else:
            raise Exception("Status code is something different 200 or 404 which is %s, "
                            "this means something really went bad, check zato server logs"
                            % r.status_code)

    def rebuild_response(self, response_data):
        """
        Rebuild response data

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        return response_data


class TcknService(ZatoService):

    def prepare_payload(self):
        return '{"tckn":"%s"}' % self.check_turkish_identity_number(self.payload)

    @staticmethod
    def check_turkish_identity_number(tckn):
        """
        Türkiye Cumhuriyeti Kimlik Numarası geçerlilik kontrolü.
        11 karakter uzunluğunda karakter dizisi olmalı.

        Args:
            tckn (str): 11 karakter uzunluğunda TCKN.

        Returns:
            str: TCKN

        """

        if not tckn:
            raise Exception("tckn can not be empty")

        if type(tckn) is not str:
            raise TypeError("tckn must be string which is %s" % type(tckn))

        if len(tckn) != 11:
            raise Exception("tckn length must be 11")

        return tckn


class HitapService(ZatoService):

    def prepare_payload(self):
        import datetime
        model = getattr(importlib.import_module(self.zato_service.module_path),
                        self.zato_service.class_name)

        payload_object = dict()

        for key in model.service_dict['fields'].values():

            if isinstance(self.payload, dict):
                value = self.payload[key]
            else:
                value = getattr(self.payload, key)
                if type(value) == datetime.date:
                    value = value.strftime("%d.%m.%Y")

            payload_object[key] = value

        payload = json.dumps(payload_object)
        return payload
