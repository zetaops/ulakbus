# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, DersEtkinligi, Role
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """
    def test_derslik_ders_programlari(self):
        """
        Derslik Ders Programı iş akışı iki adımdan oluşur.
        İlk adımda, derslikler listelenir.
        Veritabanından çekilen derslik sayısı ile response'dan derslik sayısı karşılaştılıp test edilir.

        İkinci adımda ise,
        Seçilen dersliğe ait ders programları ekrana basılır.
        Veritabanından çekilen dersliğe ait ders programi sayısı ile response'dan derslik ders programi syaısı
        karşılaştılıp test edilir.

        """
        user = User.objects.get(username="ders_programi_bolum_koordinatoru_1")
        self.prepare_client("/derslik_ders_programi", user=user)
        resp = self.client.post()
        ders_etkinlikleri = DersEtkinligi.objects.filter(solved=True)
        derslikler = [etkinlik.room for etkinlik in ders_etkinlikleri]
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(derslikler)
        resp = self.client.post(form={"ileri": 1, "derslik": "JlPb05QuhqMju6pEFNSPZwWgAxr"})
        assert "derslik_ders_programlari" in resp.json
        assert len(resp.json["derslik_ders_programlari"]["zaman_plani"]) == len(
            DersEtkinligi.objects.filter(room_id="JlPb05QuhqMju6pEFNSPZwWgAxr"))
