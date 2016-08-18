# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, SinavEtkinligi, Room
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_derslik_sinav_programlari(self):
        """
        Derslik Sınav Programları iş akışı iki adımdan oluşur.

        İlk adımda derslik seçilir.
        Veritabanından çekilen derslik sayısı ile sunucudan dönen derslik sayısı karşılaştırılıp test edilir.

        İkinci adımda seçilen dersliğe ait sınav programı getirilir.
        Veritabanından çekilen sınav etkinlikleri sayısı ile sunucudan dönen sınav etkinlikleri sayısı
        karşılaştırılıp test edilir.

        """

        user = User.objects.get(username="ders_programi_koordinatoru_1")
        self.prepare_client("/derslik_sinav_programlari", user=user)
        resp = self.client.post()
        derslikler = [s_yerleri.room for s_etkinlik in SinavEtkinligi.objects.filter(solved=True)
                      for s_yerleri in s_etkinlik.SinavYerleri if s_etkinlik.SinavYerleri]
        assert len(derslikler) == len(resp.json['forms']['form'][2]['titleMap'])
        resp = self.client.post(form={"ileri": 1, "derslik": 'XJUW0J9xEiOUqBWUtHAkky0yPjk'})
        room = Room.objects.get("XJUW0J9xEiOUqBWUtHAkky0yPjk")
        num_of_sinav_etkinlikleri = [s for s in SinavEtkinligi.objects if room in s.SinavYerleri and s.solved]
        count_of_sinav_etkinlikleri = 0
        for i in range(1, len(resp.json['objects'])):
            for day in resp.json['objects'][i]['fields']:
                if resp.json['objects'][i]['fields'][day]:
                    count_of_sinav_etkinlikleri += 1
        assert len(num_of_sinav_etkinlikleri) == count_of_sinav_etkinlikleri

