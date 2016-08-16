# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Donem, SinavEtkinligi, User, Ogrenci, OgrenciDersi, Sube
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):
    def test_okutman_sinav_programi_goruntule(self):

        user = User.objects.get(username='ogrenci_3')
        self.prepare_client('/ogrenci_sinav_programi_goruntule', user=user)
        # Giriş yapılan user'ın öğrenci objesi bulunur.
        ogrenci = Ogrenci.objects.get(user=self.client.current.user)
        guncel_donem = Donem.objects.get(guncel=True)
        # Öğrencinin güncel dönemde aldığı dersler bulunur.
        ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=guncel_donem)
        ogrenci_adi = ogrenci.ad + ' ' + ogrenci.soyad

        subeler = []
        # Bulunan öğrenci derslerinin şubeleri bulunur ve listeye eklenir.
        for ogrenci_ders in ogrenci_dersleri:
            try:
                sube = Sube.objects.get(ogrenci_ders.sube.key)
                subeler.append(sube)
            except:
                pass

        for i in range(2):
            # ogrenci_3 kullanıcısıyla giriş yapılır.
            user = User.objects.get(username='ogrenci_3')
            # testi yazılacak iş akışı seçilir.
            self.prepare_client('/ogrenci_sinav_programi_goruntule', user=user)

            # Giriş yapılan user'ın öğrenci objesi bulunur.
            ogrenci = Ogrenci.objects.get(user=self.client.current.user)
            guncel_donem = Donem.objects.get(guncel=True)
            # Öğrencinin güncel dönemde aldığı dersler bulunur.
            ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=guncel_donem)
            ogrenci_adi = ogrenci.ad + ' ' + ogrenci.soyad

            subeler = []
            # Bulunan öğrenci derslerinin şubeleri bulunur ve listeye eklenir.
            for ogrenci_ders in ogrenci_dersleri:
                try:
                    sube = Sube.objects.get(ogrenci_ders.sube.key)
                    subeler.append(sube)
                except:
                    pass

            # İlk test yayınlanmış sınav etkinliğinin olmaması durumudur.
            # Bu yüzden Sınav Etkinliği modelinin published fieldı False yapılır.
            if i == 0:
                cond = False

            # İkinci test yayınlanmış sınav etkinliğinin olması durumudur.
            # Bu yüzden Sınav Etkinliği modelinin published fieldı True yapılır.
            else:
                cond = True

            for sube in subeler:
                for sinav_etkinlik in SinavEtkinligi.objects.filter(sube=sube, donem=guncel_donem):
                    sinav_etkinlik.published = cond
                    sinav_etkinlik.save()

            time.sleep(1)

            resp = self.client.post()

            # Yayınlanmış sınav etkinliği bulunmaması durumunda Uyarı vermesi beklenir.
            if i == 0:
                assert resp.json['msgbox']['title'] == "Uyarı!"

            # Yayınlanmış sınav etkinliği olması durumunda öğretim görevlisinin adının
            # bulunduğu bir sınav takvimi gösterilmesi beklenir.
            else:
                assert ogrenci_adi in resp.json['forms']['schema']["title"]
