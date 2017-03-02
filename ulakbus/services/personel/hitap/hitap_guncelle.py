# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import ZatoHitapService
import os
import urllib2
from json import dumps

"""HITAP Guncelle Servisi

Hitap guncelle (insert) servislerinin kalıtılacağı
abstract HITAP Guncelle servisini içeren modül.


Attributes:
    H_USER (str): Hitap kullanıcı adı
    H_PASS (str): Hitap kullanıcı şifresi

"""

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HITAPGuncelle(ZatoHitapService):
    """
    Hitap Güncelleme servislerinin kalıtılacağı abstract Zato servisi.

    Güncelleme servisleri gerekli girdileri (Hitap dict, Hitap username, Hitap password)
    Hitap'a yollayıp dönecek cevabı elde etmektedir.

    Attributes:
        service_name (str): İlgili Hitap sorgu servisinin adı
        service_dict (dict): Hitap servisine yollanacak datayı hazırlamak için sözlük.
            Servise gönderilecek verinin alanlarına ait sözlüğü
            ve tarih filtresi uygulanacak ve servis tarafında gerekli olan alanların
            listesini içerir.

    """
    HAS_CHANNEL = False
