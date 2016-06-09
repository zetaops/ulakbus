# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_aktif_donem_degistirme(self):

        user = User.objects.get(username='ogrenci_isleri_1')
        self.prepare_client('/aktif_donem_degistirme', user=user)
        self.client.post()
        self.client.post(form={'kaydet': 1})
