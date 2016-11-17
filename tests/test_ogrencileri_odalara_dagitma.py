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

        # Sınav etkinliği seçilir.
        sinav_etkinligi = SinavEtkinligi.objects.get('H9mqfdqqnnBxKHgSCuX3cg0DPrI')

        # Testin düzgün çalışabilmesi için,
        # eğer varsa öğrencilerin atandığı sınav yerleri boşaltılır.
        for room in sinav_etkinligi.Ogrenciler:
            room.room = Room()
            sinav_etkinligi.save()

        # Ogrenciler list node'unda bulunan obje sayısı, veritabanındaki kayıt sayısı ile
        # aynı olup olmadığı test edilir.
        assert len(sinav_etkinligi.Ogrenciler) == OgrenciDersi.objects.filter(
            sube=sinav_etkinligi.sube, donem=sinav_etkinligi.donem).count()

        # Sınav öğrenci listesini getiren methodun çalışması kontrol edilir.
        assert len(sinav_etkinligi.sinav_ogrenci_listesi()) == len(sinav_etkinligi.Ogrenciler)

        # Etkinliğin yapılacağı odaların toplam kontenjanı bulunur.
        toplam_kontenjan = sum([e.room.capacity for e in sinav_etkinligi.SinavYerleri])

        # Toplam kontenjanın etkinliğe katılacak toplam öğrenci sayısından fazla olması
        # kontrol edilir.
        assert toplam_kontenjan >= len(sinav_etkinligi.Ogrenciler)

        # Toplam öğrenci sayısının toplam kontenjan sayısına bölümüyle
        # her bir sınıfın dengeli olmasını sağlamak için gereken doluluk oranı
        # bulunur.
        oran = sinav_etkinligi.doluluk_orani_hesapla()

        # Bulunan bu oranın 1'e eşit ya da küçük olması kontrol edilir.
        assert oran <= 1

        # Odalar öğrencilere rastgele atanır.
        SinavEtkinligi.ogrencileri_odalara_dagit(sinav_etkinligi, oran)

        # Sınavın yapılacağı sınıfların listesi elde edilir.
        sinav_yerleri_listesi = []
        for sinav_yeri in sinav_etkinligi.SinavYerleri:
            sinav_yerleri_listesi.append(sinav_yeri.room)

        sinav_yerleri = {}
        for etkinlik in sinav_etkinligi.Ogrenciler:
            # Her bir öğrencinin bir sınıfa atandığı kontrol edilir.
            assert etkinlik.room is not None
            # Atanan odaların doğru odalar olduğu kontrol edilir.
            assert etkinlik.room in sinav_yerleri_listesi
            # ogrenci_sinav_oda_getir methodunun çalışması kontrol edilir.
            assert sinav_etkinligi.ogrenci_sinav_oda_getir(etkinlik.ogrenci) in sinav_yerleri_listesi

            # Hangi odanın kaç öğrenciye atandığı bulunur.
            # sınav_yerleri_key = room.key
            # sinav_yerleri_value = integer
            if etkinlik.room.key in sinav_yerleri:
                sinav_yerleri[etkinlik.room.key] += 1
            else:
                sinav_yerleri[etkinlik.room.key] = 1

        # Odanın kapasitesinden fazla kişiye atanmadığı kontrol edilir.
        for yer in sinav_yerleri.keys():
            assert sinav_yerleri[yer] <= Room.objects.get(yer).capacity

        # Öğrenci sayısı kadar atanmış oda objesinin olduğu kontrol edilir.
        assert sum(sinav_yerleri.values()) == len(sinav_etkinligi.sinav_ogrenci_listesi())
