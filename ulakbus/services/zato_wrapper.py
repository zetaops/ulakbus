# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus import settings
import requests
import json


class ZatoService(object):
    """

    Simple zato service wrapper class. You can write your zato services extending this class.

    This class simply needs some parameter to be set as you see in init payload and service uri.
    Defaults are an empty dict for payload, string "ping" for service_uri.

    Ping service returns just 'ok' which can be used as an health check to determine zato servers is alive or not.

    ``service_uri`` and ``payload`` parameters especially is set by extending class' __init__.

    """

    def __init__(self):
        self.payload = "{}"
        self.service_uri = "ping"

    def get_uri(self):
        """

        Simply returns full uri of zato service object. It uses ``ZATO_SERVER`` from settings module.

        The ``ZATO_SERVER`` can be set as environment variable as below:
        ::

            export ZATO_SERVER='http://127.0.0.1/'


        :return: unique identification string of service on zato services including
                 join of zato server url (generally a load balancer url) and service name on zato.


        """

        return '/'.join([settings.ZATO_SERVER, self.service_uri])

    def zato_request(self):
        """

        Makes zato requests. Zato expects payloads as json over POST method and sends back json. Return json cotains
        two parts one is status and the other is result.

        Status part is can be ``ok`` or ``error`` depends on what happens in zato servers while running. Result part is
        the data part which is expected by consumer.

        :return: if requests fails, returns ``None``, or simply string of zato service response payload


        """

        uri = self.get_uri()
        payload = json.loads(self.payload)
        r = requests.post(uri, data=json.dumps(payload))
        if r.status_code == 200:
            response = r.json()
            r.close()
            try:
                if response['status'] == 'ok':
                    return response['result']
                else:
                    # all zato internal errors will be handled here, riak error, connection error etc..
                    raise Exception("your service request failed with error %s" % response['result'])
            except KeyError:
                raise Exception("your service response contains no status code, check your zato service package")

        if r.status_code == 404:
            raise Exception("Service called '%s' is not defined on zato "
                            "servers or service_uri changed" % self.service_uri)
        # other than 404 errors will be handled here, such as unauthorized requests, permission denied or etc..
        else:
            raise Exception("Status code is something different 200 or 404 which is %s, "
                            "this means something really went bad, check zato server logs" % r.status_code)


class HitapService(ZatoService):
    @staticmethod
    def check_turkish_identity_number(tckn):
        """

        Checks Turkish ID Number, if empty, not a string or different than 11 length

        :param tckn: string, 11 length
        :type tckn: str

        :return: string tckn or raises exception

        """

        if not tckn:
            raise Exception("tckn can not be empty")

        if type(tckn) is not str:
            raise TypeError("tckn must be string which is %s" % type(tckn))

        if len(tckn) != 11:
            raise Exception("tckn length must be 11")

        return tckn


class HitapHizmetCetvelGetir(HitapService):
    """

    This service takes tckn as string, consume "hizmet cetveli getir" of hitap which syncs local data on riak.

    Example
    ::

        from zato_wrapper_class import HitapHizmetCetvelGetir
        zs = HitapHizmetCetvelGetir(tckn="12345678900")
        response = zs.zato_request()

        response: list, with lines of hizmet_cetveli

    """

    def __init__(self, service_uri='hizmet-cetveli-getir', tckn=""):
        """

        :param service_uri: string, default hizmet-cetveli-getir
        :type service_uri: str

        :param tckn: string, of 11 byte length, can not be empty
        :type tckn: str

        """

        super(HitapHizmetCetvelGetir, self).__init__()
        self.service_uri = service_uri
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapHizmetCetveliSenkronizeEt(HitapService):
    """

    This service takes tckn as string, consume "hizmet cetvel senkronize et" of hitap, sync local data on riak.

    Example
    ::

        from zato_wrapper_class import HitapHizmetCetveliSenkronizeEt
        zs = HitapHizmetCetveliSenkronizeEt(tckn="12345678900")
        response = zs.zato_request()

        response: string, 'ok' for successful sync data of existent person

    """

    def __init__(self, service_uri='hizmet-cetveli-senkronize-et', tckn=""):
        """

        Takes two parameters service_uri and tckn

        :param service_uri: service name on zato, default is hizmet-cetveli-senkronize-et
        :type service_uri: str

        :param tckn: 11 byte length tckn number, can not be empty
        :type tckn: str


        """

        super(HitapHizmetCetveliSenkronizeEt, self).__init__()
        self.service_uri = service_uri
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class MernisKimlikBilgileriGetir(HitapService):
    """

    This service takes tckn as string, consume "mernis kimlik bilgileri getir" of hitap services
    and sync local data on riak.

    Example
    ::

        from zato_wrapper_class import MernisKimlikBilgileriGetir
        zs = MernisKimlikBilgileriGetir(tckn="12345678900")
        response = zs.zato_request()

        response: dict containing identity information as key value pairs

    """

    def __init__(self, service_uri='mernis-kimlik-bilgileri-getir-tckn', tckn=""):
        """

        Takes two parameters service_uri and tckn

        :param service_uri: service name on zato, default is hizmet-cetvel
        :type service_uri: str

        :param tckn: string of 11 byte length, can not be empty
        :type tckn: str

        """
        super(MernisKimlikBilgileriGetir, self).__init__()
        self.service_uri = service_uri
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)
