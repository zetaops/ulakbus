# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel, Okutman, Donem, Sube, SinavEtkinligi, User
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):
    def test_okutman_sinav_programi_goruntule(self):

        for i in range(2):
            # ogretim_elemani_2 kullanıcısıyla giriş yapılır.
            user = User.objects.get(username='ogretim_elemani_2')
            # testi yazılacak iş akışı seçilir.
            self.prepare_client('/okutman_sinav_programi_goruntule', user=user)

            # Giriş yapılan user'ın personeli bulunur.
            personel = Personel.objects.get(user=self.client.current.user)
            # Personelden ilgili öğretim görevlisi bulunur.
            okutman = Okutman.objects.get(personel=personel)
            guncel_donem = Donem.objects.get(guncel=True)
            okutman_adi = okutman.ad + ' ' + okutman.soyad
            # Öğretim görevlisinin güncel dönemde ders verdiği şubeler bulunur.
            subeler = Sube.objects.filter(okutman=okutman, donem=guncel_donem)

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
                assert okutman_adi in resp.json['forms']['schema']["title"]
