# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_ogrenci_ders_ekleme(self):
        user = User.objects.get(username='ogrenci_1')
        self.prepare_client('/ogrenci_ders_ekleme', user=user)
        resp = self.client.post()
        self.client.post(form={'ileri': 1, 'Dersler': resp.json['forms']['model']['Dersler']})
