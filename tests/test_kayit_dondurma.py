# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import OgrenciProgram, Ogrenci, User, DondurulmusKayit
from ulakbus.models.auth import Role, AbstractRole
from zengine.lib.test_utils import BaseTestCase
import time

__author__ = 'H.İbrahim Yılmaz (drlinux)'


class TestCase(BaseTestCase):
    """Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_kayit_dondurma(self):
        """Öğrenci kayıt dondurma wf test methodu.

        Kayıt dondurma iş akışının ilk adımında fakülte karar no girilir.

        Kayıt dondurma iş akışının ikinci adımında öğrenci programı seçilir.

        Seçilen öğrenciye ait veritabanından dönen öğrenci programı sayısı ile
        sunucudan dönen öğrenci program sayısının eşitliği karşılaştırılıp test edilir.

        İş akışının ikinci adımında dönemler ve kayıt dondurma tarihi seçilir.

        İş akışının üçüncü aşamasında öğrencinin soyut rolü dondurulmus_kayit olarak güncellenir ve
        danışmanına bildirim gönderilir.

        Yollanan kayıtların `DondurulmusKayit` modeline kayıt edilip edilmediği ve öğrenci kayıtlı
        olduğu programın öğrencilik statüsünün değiştirilip değiştirilmediği test edilir.

        """

        # Veritabanından ogrenci_isleri_1 seçilir
        user = User.objects.get(username='ogrenci_isleri_1')

        ogrenci_id = "RnKyAoVDT9Hc89KEZecz0kSRXRF"

        # Kullanıcıya giriş yaptırılıp iş akışı başlatılır.
        self.prepare_client('/kayit_dondur', user=user)
        resp = self.client.post(id=ogrenci_id, param="ogrenci_id", wf="kayit_dondur")

        # Öğrenciye ait programlar db'den seçilir.
        op = OgrenciProgram.objects.filter(ogrenci_id='RnKyAoVDT9Hc89KEZecz0kSRXRF')

        # Fakülte karar no girilir.
        resp = self.client.post(form={'karar_no': "562562", 'kaydet': 1})

        # Veritabanından öğrenciye ait  çekilen program sayısı ile sunucudan dönen program sayısının
        # eşitliği karşılaştırılıp test edilir.
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(op)

        # Öğrencinin kayıtlı olduğu program yollanır.
        program = {'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1}
        self.client.post(model="DondurulmusKayit", wf="kayit_dondur", form=program)

        # Kayıt dondurulacak olan donem yollanır
        donemler = {'baslangic_tarihi': "06.09.2017", 'sec': 1,
                    'Donemler': [{'aciklama': "Kayıt Dondurma",
                                  'donem': "Güz - 2017",
                                  'key': "GRc6D86egPKSrXv1eDWs39FnJpV",
                                  'secim': True}]}

        resp = self.client.post(model="DondurulmusKayit", wf="kayit_dondur", form=donemler)

        assert resp.json['msgbox']['title'] == "Öğrenci Kayıt Dondurma Başarılı"

        # Veritabanından öğrencinin kaydının dondurulmuş olup olmadığı doğrulanır.
        dondurulmus_kayit = DondurulmusKayit.objects.get(ogrenci_program_id="UEGET7qn9CDj9VEj4n0nbQ7m89d")
        assert dondurulmus_kayit

        ogrenci_program = OgrenciProgram.objects.get("UEGET7qn9CDj9VEj4n0nbQ7m89d")
        assert ogrenci_program.ogrencilik_statusu == 2

        # Değişiklikler geri alınır.
        dondurulmus_kayit.blocking_delete()
