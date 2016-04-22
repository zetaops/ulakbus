# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import *
from ulakbus.models import Ders, User
import os
import time


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ders_subelendirme(self):
        """
        Ders şubelendirme iş akışını test eder.

        """

        # Bölüm başkanı kullanıcısı seçilir.
        usr = User.objects.get('RIy95nnzpqfQKTjRVxfwR5yzWSx')
        time.sleep(2)

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/ders_hoca_sube_atama', user=usr)
        self.client.post()

        # Program seçer.
        resp = self.client.post(cmd='ders_sec',
                                form=dict(program='HUqZl1XUBlFcI3G1iAegLtmlL65', sec=1))
        assert 'objects' in resp.json

        # Şubelenilecek ders seçilir.
        self.client.post(cmd='ders_okutman_formu',
                         sube='XERlRTgNiNwwm3P00sMoLv48hLh',
                         filter=dict())

        # Şubelendirme formu doldurulur.
        sube = [{'okutman': "Gqd3E8FbKYTf2olEcrPSfrlUjJT", 'kontenjan': 34, 'dis_kontenjan': 45, 'ad': "Sube 1"}]
        # Formu kaydedip ders seçim ekranına döner.
        self.client.post(cmd='subelendirme_kaydet',
                         flow='ders_okutman_formu',
                         form=dict(program_sec='null', kaydet_ders=1, bilgi_ver='null', Subeler=sube))

        # Şubelenilecek ders seçilir.
        resp = self.client.post(cmd='ders_okutman_formu',
                                sube='X6Gr2FLbIXcdwNpKZZmvPNzeA23',
                                filter=dict())

        # Dersin ismi veritabanından çekilir.
        ders = Ders.objects.get('X6Gr2FLbIXcdwNpKZZmvPNzeA23')

        assert ders.ad in resp.json['forms']['schema']['title']

        # Şubelendirme formu doldurulur.
        sube = [{'okutman': "AtxxhSfiw5xk2voeVkarxAtyYvm", 'kontenjan': 30, 'dis_kontenjan': 5, 'ad': "Sube 2"}]

        # Hocalara bilgilendirme mesajı gönderilir.
        # İş akışı bu adımdan sonra sona erer.
        resp = self.client.post(cmd='subelendirme_kaydet',
                                flow='bilgi_ver',
                                form=dict(program_sec='null', kaydet_ders='null', bilgi_ver=1, Subeler=sube))

        assert 'msgbox' in resp.json
