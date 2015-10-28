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


def zato_request(service_uri, payload):
    """
    zato request wrapper, takes zato service uri and payload.
    if response status code is 200, it returns response text else simply None
    :param service_uri: uri of service
    :param payload: payload string
    :return: return if fails None, or simply return string of zato service response payload
    """
    url = '/'.join([settings.ZATO_SERVER, service_uri])
    payload = json.loads(payload)
    r = requests.post(url, data=json.dumps(payload))
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
        raise Exception("Service called '%s' is not defined on zato servers or service_uri changed" % service_uri)
    # other than 404 errors will be handled here, such as unauthorized requests, permission denied or etc..
    else:
        raise Exception("Status code is something different 200 or 404 which is %s, "
                        "this means something really went bad, check zato server logs" % r.status_code)


def kimlik_no(tckn):
    if tckn is None:
        raise Exception("tckn can not be empty")

    if type(tckn) is not str:
        raise TypeError("tckn must be string which is %s" % type(tckn))

    if len(tckn) != 11:
        raise Exception("tckn length must be 11")

    return tckn


def hitap_hizmet_cetveli_getir(service_uri='hizmet-cetveli-getir', tckn=None):
    """
    this service takes tckn as string, consume "hizmet cetveli getir" of hitap which syncs local data on riak.

    :param service_uri: string, default hizmet-cetveli-getir
    :param tckn: string, of 11 byte length, can not be empty
    :return: list, with lines of hizmet_cetveli
    """

    payload = '{"personel":{"tckn":"%s"}}' % kimlik_no(tckn)
    return zato_request(service_uri, payload)


def hitap_hizmet_cetveli_senkronize_et(service_uri='hizmet-cetveli-senkronize-et', tckn=None):
    """
    this service takes tckn as string, consume "hizmet cetvel senkronize et" of hitap, sync local data on riak.

    :param service_uri: string, default hizmet-cetvel
    :param tckn: string of 11 byte length, can not be empty
    :return: string, 'ok' for successful sync data of existent person
    """

    payload = '{"personel":{"tckn":"%s"}}' % kimlik_no(tckn)
    return zato_request(service_uri, payload)
