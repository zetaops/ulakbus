# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPSSS

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_sss_goruntule(self):
        yayinlanmis_sss_sayisi = BAPSSS.objects.all(yayinlanmismi=True).count()
        self.prepare_client('/bap_sss', username='ulakbus')
        resp = self.client.post()
        assert yayinlanmis_sss_sayisi == len(resp.json['objects']) - 1
        assert resp.json['object_title'] == 'BAP Sıkça Sorulan Sorular'
