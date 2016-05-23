# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2016 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, Personel
from zengine.lib.test_utils import BaseTestCase

__author__ = 'Mithat Raşit Özçıkrıkcı'


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_terfisi_tikanan_personel(self):
        """
        generic_reporter iş akışı başlatıldıktan sonra;
        Terfisi duran personeller listelinir.
        Sunucudan dönen terfisi tıkanan personel sayısı ile veritabanından çekilen
        terfisi tıkanan personel sayıları karşılaştırlıp test edilir.

        """

        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("generic_reporter", user=user)
        res = self.client.post(model="TerfisiTikananPersonel")
        p_query = Personel.objects.set_params(
            fq="{!frange l=0 u=0 incu=true}sub(gorev_ayligi_derece,kadro_derece)").filter(
            gorev_ayligi_kademe__gte=4)
        assert "object" in res.json
        assert len(res.json["object"]["fields"]) == len(p_query)
