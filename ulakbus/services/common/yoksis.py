# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from zato.server.service import Service
from ulakbus import settings

UID = settings.UID

DEBUG = False
if DEBUG:
    import logging

    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    logging.getLogger('suds.transport').setLevel(logging.DEBUG)
    logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)
    logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)


class YOKSIS(Service):
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
            'ogrenim_suresi': birim.OGRENIM_SURESI
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

    def handle(self):
        birim_id = self.request.payload['birim_id']
        self.birim = self.cli.service.IDdenBirimAdiGetir(birim_id)
        return self.birim_detaylari()


class BirimAgaci(YOKSIS):
    """
    YOKSIS BirimAgaci Kaydet Servisi
    """

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

    def handle(self):
        if self.request.raw_request:
            root_unit = self.request.raw_request
        else:
            root_unit = 0
        conn = self.connection()
        self.bir(conn, root_unit=root_unit)


class DumpUnitsToUnitModel(BirimAgaci):
    """
     Dump All Units To Ulakbus auth.Unit Model by UID.
     """

    def handle(self):
        if self.request.raw_request:
            root_unit = self.request.raw_request
        else:
            root_unit = 0
        conn = self.connection()
        self.bir(conn, root_unit=UID)

    def birim_kaydet(self, birim_id):
        # self.kvdb.conn.set(birim_id, self.birim_detaylari())
        # self.logger.info("%s icin degerler: %s\n\n" % (birim_id, self.birim_detaylari()))
        from ulakbus.models.auth import Unit
        y = yoksis_birim.get(str(birim_id))
        data = self.birim_detaylari()
        u = Unit.objects.get_or_create(yoksis_no=birim_id)
        u.name = data['birim_adi']
        u.long_name = data['birim_uzun_adi']
        u.city_code = data['il_kodu']
        u.district_code = data['ilce_kodu']
        u.language = data['ogrenim_dili']
        u.english_name = data['birim_adi_ingilizce']
        u.parent_unit_no = data['bagli_oldugu_birim_id']
        u.learning_duration = data['ogrenim_suresi']
        u.osym_code = data['klavuz_kodu']
        u.learning_type = data['ogrenim_turu']
        u.unit_type = data['birim_turu_adi']
        u.is_academic = True
        u.current_situation = data['aktif']
        u.is_active = False if u.current_situation in ['Kapalı', 'Pasif'] else True
        u.uid = UID
        u.save()
