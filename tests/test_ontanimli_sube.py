# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Ders, Sube
import time
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ontanimli_sube(self):
        """
        Yeni bir ders kaydı yaratılılıp kaydedildiğinde derse
        default olarak şube atanır.

        Kaydedilmeden önce pre_save metotu ile ders nesnenin
        var olup olmadığı belirlenir.

        Kaydedildikten sonra post_save metotu ile ontanimli_sube_olustur
        metotu çağrılır.

        Bu metot ontanimli degerler ile yeni bir şube oluşturur.

        Ders modelinde tanımlı ontanimli_kontenjan, ontanimli_dis_kontenjan
        fieldlarının değerleri yeni yaratılan şubenin kontenjan ve dış
        kontenjan fieldlarına atanır.

        Ders nesnesi yaratıldığında ontanimli_kontenjan, ontanimli_dis_kontenjan
        fieldlarına herhengi bi değer atanmamışsa field içinde tanımlı
        default değeri atanır.

        """
        ders = Ders()
        ders.ad = 'Havacılık'
        ders.kod = '555'
        ders.save()
        time.sleep(1)
        assert ders.just_created
        sube = Sube.objects.get(ders_id=ders.key)
        assert sube.ad == 'Varsayılan Şube'
        assert sube.kontenjan == 30
        assert sube.dis_kontenjan == 5

        ders.delete()
        sube.delete()
