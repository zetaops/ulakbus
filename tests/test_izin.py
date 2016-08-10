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
from dateutil.relativedelta import relativedelta
from zengine.lib.test_utils import BaseTestCase
import datetime

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
        personel = Personel.objects.get(personel_id)

        # İlgili personel seçilerek wf başlatılır
        resp = self.client.post(id=personel_id, model="Izin", param="personel_id", wf="izin")
        #assert len(resp.json["object"]["fields"]) == 6

        izin_baslangic = datetime.date.today().strftime("%d.%m.%Y")
        izin_bitis = datetime.date.today() + relativedelta(days=5)
        izin_bitis = izin_bitis.strftime("%d.%m.%Y")
        # İzin alacak olan personelin yerine vekil olarak bırakacağı personelin id si
        vekil_personel_id = "YpMvzcYw3msFu79V7BfSzvNjAng"
        vekil_personel = Personel.objects.get(vekil_personel_id)

        self.client.post(cmd="yeni_izin", wf="izin")

        # Test için gerekli querylerde kullanılmak üzere oluşturulan izin başlama ve bitiş tarihleri
        test_baslangic_tarih = datetime.date.today()
        test_bitis_tarih = test_baslangic_tarih + relativedelta(days=5)

        # Belirlediğimiz kriterlerdeki izin sayısını çekiyoruz (Kayıt işleminden önce oluşturulmuş)
        eski_izin_sayisi = Izin.objects.filter(
            baslangic=test_baslangic_tarih,
            bitis=test_bitis_tarih,
            personel = personel,
            vekil=vekil_personel
        ).count()

        # Yeni izin kaydediliyor
        self.client.post(cmd="kaydet", wf="izin", form=dict(tip=1, baslangic=izin_baslangic, bitis=izin_bitis,
                                                 onay=izin_baslangic, adres="Konya", telefon="111",
                                                 vekil_id=vekil_personel_id))

        # Belirlediğimiz kriterlerdeki izin sayısını çekiyoruz (Tüm kayıtlar)

        yeni_izin_sayisi = Izin.objects.filter(
            baslangic=test_baslangic_tarih,
            bitis=test_bitis_tarih,
            personel = personel,
            vekil=vekil_personel
        ).count()

        # Yeni izin kaydının oluşturulup oluşturulmadığı kontrol ediliyor.
        assert yeni_izin_sayisi > eski_izin_sayisi