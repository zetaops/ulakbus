# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import FormData
from ulakbus.models.auth import User
from ulakbus.models.personel import Izin, Personel
from datetime import date
from dateutil.relativedelta import relativedelta
from zengine.lib.test_utils import BaseTestCase

__author__ = 'Mithat Raşit Özçıkrıkcı'

class TestCase(BaseTestCase):
    """
        İzin wf için BaseTestCase extend edilerek oluşturulmuştur
    """

    def test_yillik_izin(self):
        """
         Personel izin durumu görüntüleme ve yeni izin tanımlama işlemi için yazılmış test metoddur.
        """

        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/izin", user=user)

        # İzin işlemi yapılacak personel id
        personel_id = "ShW15GBQCCUAuk64ZrK9myA470y"

        # İlgili personel seçilerek wf başlatılır
        resp = self.client.post(id=personel_id, model="Personel", param="personel_id", wf="izin")
        #assert len(resp.json["object"]["fields"]) == 6

        izin_baslangic = date.today()
        izin_bitis = izin_baslangic + relativedelta(days=5)
        # İzin alacak olan personelin yerine vekil olarak bırakacağı personelin id si
        vekil_personel_id = "YpMvzcYw3msFu79V7BfSzvNjAng"
        vekil_personel = Personel.objects.get(vekil_personel_id)

        self.client.post(cmd="yeni_izin", wf="izin")

        # Yeni izin kaydediliyor
        self.client.post(cmd="kaydet", wf="izin", form=dict(tip=1, baslangic=izin_baslangic, bitis=izin_bitis,
                                                 onay=izin_baslangic, adres="Konya", telefon="111",
                                                 vekil_id=vekil_personel_id))

        # Yeni izin kaydının yapılıp yapılmadığı izin verileri girilerek veritabanından get metoduyla sorgulanıyor.
        # Bir sorun oluşup yeni izin kaydının yapılmaması durumunda pyokonun ObjectDoesNotExist hatası fırlatması
        # beklenmektedir.

        yeni_izin = Izin.objects.get(
         personel_id = personel_id,
         baslangic = izin_baslangic,
         bitis = izin_bitis,
         vekil_personel_id = vekil_personel_id
        )