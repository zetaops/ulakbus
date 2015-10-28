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
    r = requests.post(url, data=payload)
    if r.status_code is '200':
        response = r.json()
        r.close()
        return response['result']
    if r.status_code is '404':
        return '404'
    else:
        return None


def hitap_hizmet_cetveli_getir(service_uri='hizmet-cetvel', tckn=None):
    """
    this service takes tckn as string, consume hizmet_cetvel of hitap, sync local data on riak.

    :param service_uri: string, default hizmet-cetvel
    :param tckn: string of 11 byte length, can not be empty
    :return: if request fails None, or simply return string
             'ok' for successful sync data of existent person
             'new' for successful sync data of new person
             'connection error' for zato internal error
             'riak error' for zato riak connection error
             '404' for not found services on zato servers, check service_uri
    """
    if tckn is None:
        return "tckn couldn't be empty"

    if len(tckn) == 11:
        payload = '{"personel":{"tckn":"%s"}}' % tckn
        response = zato_request(service_uri, json.dumps(payload))
        return response
    else:
        return "check tckn"
