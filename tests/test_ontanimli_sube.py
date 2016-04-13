# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import Ders, Sube
import time

class TestCase(BaseTestCase):
    """
    Bu sınıf
    """
    def test_ontanimli_sube(self):
        ders = Ders()
        ders.ad = 'Havacılık'
        ders.kod = '555'
        ders.save()
        time.sleep(2)
        assert ders.just_created
        sube = Sube.objects.get(ders=ders)
        assert sube.ad == 'Varsayılan Şube'
        # sube için tanımlı default değerine ulaşamıyorum. Sıfır dönüyor
        print  sube.kontenjan


