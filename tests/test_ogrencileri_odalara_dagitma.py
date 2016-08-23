# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import SinavEtkinligi, Room, OgrenciDersi
from zengine.lib.test_utils import BaseTestCase

class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ogrencileri_odalara_dagitma(self):
        """
        Sınav etkinliklerine katılacak öğrencilerin sınavlara girecekleri odalara
        rastgele atanmasının testi.


        """

        sinav_etkinligi = SinavEtkinligi.objects.filter()[0]

        assert len(sinav_etkinligi.Ogrenciler) == OgrenciDersi.objects.filter(sube = sinav_etkinligi.sube,donem = sinav_etkinligi.donem).count()

        toplam_kontenjan = 0
        for sinav_yeri in sinav_etkinligi.SinavYerleri:
            toplam_kontenjan += sinav_yeri.room.capacity

        assert toplam_kontenjan > len(sinav_etkinligi.Ogrenciler)

        oran = SinavEtkinligi.doluluk_orani_hesapla(sinav_etkinligi)

        assert oran < 1

        SinavEtkinligi.ogrencileri_odalara_dagit(sinav_etkinligi,oran)

        sinav_yerleri_listesi = []
        for sinav_yeri in sinav_etkinligi.SinavYerleri:
            sinav_yerleri_listesi.append(sinav_yeri.room)
        sinav_yerleri = {}
        for etkinlik in sinav_etkinligi.Ogrenciler:
            assert etkinlik.room is not None
            assert etkinlik.room in sinav_yerleri_listesi
            sinav_yerleri[etkinlik.room.key] += 1 if etkinlik.room.code in sinav_yerleri else 1

        for yer in sinav_yerleri.keys():
            assert sinav_yerleri[yer] <= Room.objects.get(sinav_yerleri[yer]).capacity