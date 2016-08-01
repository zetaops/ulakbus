# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel, Okutman, Donem, Unit, SinavEtkinligi, User
from zengine.lib.test_utils import BaseTestCase
import time

class TestCase(BaseTestCase):
    def test_okutman_sinav_programi_goruntule(self):

        for i in range(2):
            user = User.objects.get(username='ogretim_elemani_2')
            self.prepare_client('/okutman_sinav_programi_goruntule', user=user)

            personel = Personel.objects.get(user=self.client.current.user)
            okutman = Okutman.objects.get(personel=personel)
            guncel_donem = Donem.objects.get(guncel=True)
            okutman_birim = Unit.objects.get(yoksis_no=self.client.current.role.unit.yoksis_no)
            okutman_adi = okutman.ad +' '+ okutman.soyad

            if i == 0:
                cond = False
            else:
                cond = True

            for sinav_etkinlik in SinavEtkinligi.objects.filter(bolum=okutman_birim, donem=guncel_donem):
                sinav_etkinlik.published = cond
                sinav_etkinlik.save()

            resp = self.client.post()

            if i == 0:
                assert resp.json['msgbox']['title'] == "Uyarı!"

            else:
                assert okutman_adi in resp.json['forms']['schema']["title"]