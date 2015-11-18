# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from zato.server.service import Service
import urllib2
import json
from lxml.builder import E
from lxml import etree
from lxml import objectify
from ulakbus.models import Ogrenci

from ulakbus.models import Banka
from ulakbus.models import BankaAuth

from ulakbus.models import Borc
from ulakbus.models import Odeme


class Banka(Service):
    def authenticate(self):
        return True
        try:
            BankaAuth.object.get(username=self.bank_username, password=self.bank_password)
            return True
        except:
            return False


class Borc(Banka):
    """
    Banka Borc Sorgulama Soap Servisi
    """

    def handle(self):
        root = self.request.payload
        banka_kodu = root.BankaKodu.text
        sube_kodu = root.SubeKodu.text
        kanal_kodu = root.KanalKodu.text
        mesaj_no = root.MesajNo.text
        username = root.KullaniciKodu.text
        password = root.KullaniciSifresi.text
        ogrenci_no = root.OgrenciNo.text

        resp = etree.Element('response')

        if self.authenticate():
            objectify.SubElement(resp, 'BankaKodu').text(banka_kodu)
            objectify.SubElement(resp, 'SubeKodu').text(sube_kodu)
            objectify.SubElement(resp, 'KanalKodu').text(kanal_kodu)
            objectify.SubElement(resp, 'MesajNo').text(mesaj_no)
            objectify.SubElement(resp, 'KullaniciKodu').text(username)
            objectify.SubElement(resp, 'KullaniciSifresi').text(password)
            objectify.SubElement(resp, 'OgrenciNo').text(ogrenci_no)
            borclar = objectify.SubElement(resp, 'borclar')

            ogr = Ogrenci.objects.get(ogrenci_no=ogrenci_no)

            for b in Borc.objects.filter(ogrenci=ogr):
                borc = objectify.SubElement(borclar, 'borc')
                objectify.SubElement(borc, 'UcretTuru').text(b.ucret_turu)
                objectify.SubElement(borc, 'TahakkukReferansNo').text(b.tahakkuk_referans_no)
                objectify.SubElement(borc, 'SonOdemeTarihi').text(b.son_odeme_tarihi)
                objectify.SubElement(borc, 'Borc').text(b.borc)
                objectify.SubElement(borc, 'BorcAck').text(b.borc_ack)
        else:
            resp = E.respose(E.hata('Ogrenci Yok'))

        self.response.payload = etree.tostring(resp)
