# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from ulakbus.models import User, Personel
from zengine.lib.test_utils import BaseTestCase
import datetime


class TestCase(BaseTestCase):
    def test_gorev_suresi_biten_personel(self):
        """
            Görev süresi dolan personel raporu sorgulanır.
        """
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("generic_reporter", user=user)
        res = self.client.post(model="GorevSuresiBitenPersonel")

        personeller = Personel.objects.filter(
            gorev_suresi_bitis__lte=datetime.date(2016, 5, 24) + datetime.timedelta(days=120),
            personel_turu=1
        )

        assert len(res.json["object"]["fields"]) == len(personeller)
