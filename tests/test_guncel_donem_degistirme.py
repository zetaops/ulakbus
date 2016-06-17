# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User, Donem
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_guncel_donem_degistirme(self):
        """
        Güncel Dönem Değiştirme iş akışında güncel dönem seçilir,
        kaydedilir, bilgi verilir.
        Seçilen dönemin güncel dönem olarak kaydedilip kaydedilmediği test edilir.
        Sunucudan dönen cevapta msgboz olup olmadığı test edilir.

        """

        # ögrenci_isleri_1 kullanıcısı seçilir.
        user = User.objects.get(username='ulakbus')

        # guncel_donem_degistirme iş akışı başlatılır.
        self.prepare_client('/guncel_donem_degistirme', user=user)
        self.client.post()

        # Seçilen dönem
        secilen_guncel_donem_key = 'SBx09BKCv86hp53HGVT2i7vBxGN'

        # Yeni dönem seçilir ve kaydedilir.
        resp = self.client.post(form={'guncel_donem': secilen_guncel_donem_key, 'kaydet': 1})
        time.sleep(1)

        # Güncel dönem olarak kaydedilip kaydedilmediği test edilir.
        assert Donem.guncel_donem().key == secilen_guncel_donem_key

        assert 'msgbox' in resp.json
