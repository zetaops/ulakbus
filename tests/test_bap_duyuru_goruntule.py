# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPDuyurular

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_duyuru_goruntule(self):
        yayinlanan_duyuru_sayisi = BAPDuyurular.objects.all(yayinlanmismi=True).count()
        self.prepare_client('/bap_duyurulari_goruntule', username='ulakbus')
        resp = self.client.post()
        assert yayinlanan_duyuru_sayisi == len(resp.json['objects']) - 1
        assert resp.json['object_title'] == 'BAP Genel Duyurular'
