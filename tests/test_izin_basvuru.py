# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'H.İbrahim Yılmaz (drlinux)'

import time
from ulakbus.models import User, Izin, Personel
from ulakbus.models.form import FormData
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_izin_basvuru(self):
        """İzin basvuru wf test methodu.

        İzin basvuru iş akışının ilk adımında personele izin başvuru formu gösterilir.

        Personelin formu doldurup kaydetmesi beklenir.

        Veritabanında FormData Modelinde ilgili formun kaydının olup olmadığı sorgulanır.

        """

        # veritabanından test_user seçilir
        usr = User.objects.get(username='test_user')
        time.sleep(1)
        personel = Personel.objects.get(user=usr)

        personel_id = personel.key

        # izin_basvuru WF çalıştırılır
        self.prepare_client('/izin_basvuru', user=usr)
        self.client.post()
        izin_data = {"izin_adres": "izin adresim", "izin_ait_yil": "2015",
                     "izin_baslangic": "18.04.2016", "izin_bitis": "30.04.2016", "izin_turu": "3"}
        resp = self.client.post(param="personel_id", id=personel_id, form=izin_data)

        time.sleep(3)

        formdata = FormData.objects.filter(user=usr)

        assert len(formdata) > 0
