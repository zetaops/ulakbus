# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from zato.server.service import Service

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
            'birim_adi': birim.BIRIM_ADI.encode('utf-8'),
            'birim_id': birim.BIRIM_ID,
            'birim_uzun_adi': birim.BIRIM_UZUN_ADI.encode('utf-8'),
            'il_kodu': birim.IL_KODU,
            'ogrenim_turu': birim.OGRENIM_TURU.encode('utf-8'),
            'bagli_oldugu_birim_id': birim.BAGLI_OLDUGU_BIRIM_ID,
            'birim_turu_adi': birim.BIRIM_TURU_ADI.encode('utf-8'),
            'ilce_kodu': birim.ILCE_KODU,
            'klavuz_kodu': birim.KILAVUZ_KODU,
            'ogrenim_suresi': birim.OGRENIM_SURESI
        }
        if birim.OGRENIM_DILI:
            ret.update({'ogrenim_dili': birim.OGRENIM_DILI.encode('utf-8')})
        if birim.BIRIM_ADI_INGILIZCE:
            ret.update({'birim_adi_ingilizce': birim.BIRIM_ADI_INGILIZCE.encode('utf-8')})

        return ret

    def birim_kaydet(self, birim_id):
        # self.kvdb.conn.set(birim_id, self.birim_detaylari())
        self.logger.info("%s icin degerler: %s\n\n" % (birim_id, self.birim_detaylari()))

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

    def handle(self):
        c = self.connection()

        def bir(b=0):
            # walk through alt birimler
            # start from 0
            self.birim = c.service.IDdenBirimAdiGetir(b)
            if b != 0:
                self.birim_kaydet(birim_id=b)

            alt_birimler = c.service.AltBirimleriGetir(b)
            alt_birimler = alt_birimler[1].Birimler
            if len(alt_birimler) > 0:
                for b in alt_birimler:
                    if b is None:
                        continue
                    else:
                        bir(b.BIRIM_ID)

        bir()