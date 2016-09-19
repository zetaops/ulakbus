# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_ogrenci_basari_durumu(self):

        usr = User.objects.get(username='ogrenci_1')
        self.prepare_client('/ogrenci_basari_durumu', user=usr)
        resp = self.client.post()
        assert len(resp.json['objects'][0]['objects']) == 11
        assert resp.json['objects'][0]['objects'][1]['fields'][4] == "50.00"
