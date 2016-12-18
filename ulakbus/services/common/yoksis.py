# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
from ulakbus import settings

__author__ = 'Ali Riza Keles'

UID = settings.UID

DEBUG = False
if DEBUG:
    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    logging.getLogger('suds.transport').setLevel(logging.DEBUG)
    logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)


class YOKSIS(UlakbusService):

    HAS_CHANNEL = False

    def __init__(self):
        super(YOKSIS, self).__init__()
        self.cli = self.connection()
        self.birim = 0

    @staticmethod
    def connection():
        """
        Bu metod Zato suds proxy kullanimi icin patch yapilana kadar burada duracak.
        :return: suds client
        """

        # conn = self.outgoing.soap['YOKSIS Akademik Birim Agaci'].conn
        # cli = conn.client()

        from suds.client import Client
        from suds.cache import NoCache
        wsdl = 'http://servisler.yok.gov.tr/ws/UniversiteBirimlerv1?WSDL'
        proxy = {'http': 'services.konya.edu.tr:3128'}
        cli = Client(wsdl, cache=NoCache(), proxy=proxy)
        cli.set_options(faults=False)
        return cli

    def birim_detaylari(self):
        birim = self.get_birim_from_returned_tuple()
        ret = {
            'aktif': birim.AKTIF,
            'birim_adi': birim.BIRIM_ADI,
            'birim_id': birim.BIRIM_ID,
            'birim_uzun_adi': birim.BIRIM_UZUN_ADI,
            'il_kodu': birim.IL_KODU,
            'ogrenim_turu': birim.OGRENIM_TURU,
            'bagli_oldugu_birim_id': birim.BAGLI_OLDUGU_BIRIM_ID,
            'birim_turu_adi': birim.BIRIM_TURU_ADI,
            'ilce_kodu': birim.ILCE_KODU,
            'klavuz_kodu': birim.KILAVUZ_KODU,
            'ogrenim_suresi': birim.OGRENIM_SURESI,
            'ogrenim_dili': '',
            'birim_adi_ingilizce': ''
        }
        if birim.OGRENIM_DILI:
            ret.update({'ogrenim_dili': birim.OGRENIM_DILI})
        if birim.BIRIM_ADI_INGILIZCE:
            ret.update({'birim_adi_ingilizce': birim.BIRIM_ADI_INGILIZCE})

        return ret

    def birim_detaylari_utf8(self):
        detaylar = self.birim_detaylari()
        for k, v in detaylar:
            if v is not '' and type(v) is 'str':
                detaylar[k] = v.encode('utf-8')
        return detaylar

    def birim_kaydet(self, birim_id):
        # self.kvdb.conn.set(birim_id, self.birim_detaylari())
        # self.logger.info("%s icin degerler: %s\n\n" % (birim_id, self.birim_detaylari()))
        from pyoko.db.connection import client
        yoksis_birim = client.bucket_type('catalog').bucket('ulakbus_yoksis_birim')

        y = yoksis_birim.get(str(birim_id))
        data = self.birim_detaylari()
        y.data = data
        # print("%s: stored.." % (birim_id))
        self.logger.info("%s icin kaydedildi: \n\n" % birim_id)
        y.store()

    def get_birim_from_returned_tuple(self):
        return self.birim[1][0]


class BirimDetay(YOKSIS):
    """
    YOKSIS Birim Detay Zato Servisi
    """

    HAS_CHANNEL = True

    def handle(self):
        birim_id = self.request.payload['birim_id']
        self.birim = self.cli.service.IDdenBirimAdiGetir(birim_id)
        return self.birim_detaylari()


class BirimAgaci(YOKSIS):
    """
    YOKSIS BirimAgaci Kaydet Servisi
    """

    HAS_CHANNEL = True

    def bir(self, conn, root_unit):
        # walk through alt birimler
        # start from 0
        self.birim = conn.service.IDdenBirimAdiGetir(root_unit)
        if root_unit != 0:
            self.birim_kaydet(birim_id=root_unit)

        alt_birimler = conn.service.AltBirimleriGetir(root_unit)
        alt_birimler = alt_birimler[1].Birimler
        if len(alt_birimler) > 0:
            for b in alt_birimler:
                if b is None:
                    continue
                else:
                    self.bir(conn, root_unit=b.BIRIM_ID)

    def handle(self):
        c = self.connection()
        self.bir(c, root_unit=0)


class DumpAllUnitsToRiak(BirimAgaci):
    """
    Dump All Units To Riak by root unit id. If scheduler's self.request.raw_request is empty, then root_unit = 0
    This service runs every night at 03.14 am to sync yoksis data for all universities.
    """

    HAS_CHANNEL = True

    def handle(self):
        if self.request.raw_request:
            root_unit = self.request.raw_request
        else:
            root_unit = 0
        conn = self.connection()
        self.bir(conn, root_unit=root_unit)


class DumpUnitsToUlakbusUnitModel(BirimAgaci):
    """
     Dump All Units To Ulakbus auth.Unit Model by UID.
     """

    HAS_CHANNEL = True

    def handle(self):

        if self.request.raw_request:
            root_unit = self.request.raw_request
        else:
            root_unit = UID
        conn = self.connection()
        self.bir(conn, root_unit=root_unit)

    def birim_kaydet(self, birim_id):
        from ulakbus.models.auth import Unit
        data = self.birim_detaylari()
        u, is_new = Unit.objects.get_or_create(yoksis_no=birim_id)

        u.name, should_save = (u.name, False) if u.name == data['birim_adi'] else (data['birim_adi'], True)
        u.long_name, should_save = (u.long_name, False) if u.name == data['birim_uzun_adi'] else (
            data['birim_uzun_adi'], True)
        u.city_code, should_save = (u.city_code, False) if u.name == data['il_kodu'] else (data['il_kodu'], True)
        u.district_code, should_save = (u.district_code, False) if u.name == data['ilce_kodu'] else (
            data['ilce_kodu'], True)
        u.language, should_save = (u.language, False) if u.name == data['ogrenim_dili'] else (
            data['ogrenim_dili'], True)
        u.english_name, should_save = (u.english_name, False) if u.name == data['birim_adi_ingilizce'] else (
            data['birim_adi_ingilizce'], True)
        u.parent_unit_no, should_save = (u.parent_unit_no, False) if u.name == data['bagli_oldugu_birim_id'] else (
            data['bagli_oldugu_birim_id'], True)
        u.learning_duration, should_save = (u.learning_duration, False) if u.name == data['ogrenim_suresi'] else (
            data['ogrenim_suresi'], True)
        u.osym_code, should_save = (u.osym_code, False) if u.name == data['klavuz_kodu'] else (
            data['klavuz_kodu'], True)
        u.learning_type, should_save = (u.learning_type, False) if u.name == data['ogrenim_turu'] else (
            data['ogrenim_turu'], True)
        u.unit_type, should_save = (u.unit_type, False) if u.name == data['birim_turu_adi'] else (
            data['birim_turu_adi'], True)

        new_situation = False if data['aktif'] in ['Kapalı', 'Pasif'] else True
        u.is_active, should_save = (u.is_active, False) if u.is_active == new_situation else (new_situation, True)

        u.is_active = False if u.current_situation in ['Kapalı', 'Pasif'] else True

        if is_new or should_save:
            u.is_academic = True
            u.uid = UID
            u.save()
