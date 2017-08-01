# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_etkinlik_basvuru_degerlendir(self):
        etkinlik_id = 'BI8I3XZIiThvvrBZM2EoejWq4bT'
        user = User.objects.get(username='ogretim_elemani_2')

        self.prepare_client('/bap_etkinlik_basvuru_degerlendir', user=user)
        self.client.post()
