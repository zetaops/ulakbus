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

        Kayıt dondurma iş akışının ilk adımında öğrenci programı seçilir.

        Seçilen öğrenciye ait veritabanından dönen öğrenci programı sayısı ile
        sunucudan dönen öğrenci program sayısının eşitliği karşılaştırılıp test edilir.

        İş akışının ikinci adımında dönemler ve kayıt dondurma tarihi seçilir.

        İş akışının üçüncü aşamasında öğrencinin soyut rolü dondurulmus_kayit olarak güncellenir ve
        danışmanına bildirim gönderilir.

        Yollanan kayıtların `DondurulmusKayit` modeline kayıt edilip edilmediği ve oğrenciye ait
        soyut rolün dondurulmus_kayit olup olmadığına bakılır.

        """

        # Veritabanından ogrenci_isleri_1 seçilir
        usr = User.objects.get(username='ogrenci_isleri_1')
        time.sleep(1)

        ogrenci_id = "RnKyAoVDT9Hc89KEZecz0kSRXRF"

        # Kayit_dondur wF çalıştırılır
        self.prepare_client('/kayit_dondur', user=usr)
        resp = self.client.post(id=ogrenci_id, model="DondurulmusKayit", param="ogrenci_id",
                                wf="kayit_dondur")

        # Öğrenciye ait programlar db'den seçilir.
        op = OgrenciProgram.objects.filter(ogrenci_id='RnKyAoVDT9Hc89KEZecz0kSRXRF')
        ogrenci = Ogrenci.objects.get(ogrenci_id)

        # Veritabanından öğrenciye ait  çekilen program sayısı ile sunucudan dönen program sayısının
        # eşitliği karşılaştırılıp test edilir.
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(op)

        # Ögrencinin kayıtlı olduğu program yollanır
        program = {'program': "UEGET7qn9CDj9VEj4n0nbQ7m89d", 'sec': 1}
        self.client.post(model="DondurulmusKayit", wf="kayit_dondur", form=program)

        # Kayıt dondurulacak olan donem yollanır
        donemler = {'baslangic_tarihi': "06.03.2016", 'sec': 1,
                    'Donemler': [{'aciklama': "kayit dondurma test",
                                  'donem': "Güz - 2017",
                                  'key': "GRc6D86egPKSrXv1eDWs39FnJpV",
                                  'secim': True}]}

        resp = self.client.post(model="DondurulmusKayit", wf="kayit_dondur", form=donemler)

        # Sonucu doğrula
        assert resp.json['msgbox']['title'] == "Öğrenci Kayıt Dondurma Başarılı"

        time.sleep(1)

        # Veritabanından ogrencinin kaydının dondurulmuş olup olmadığı doğrulanır
        d_kayit = DondurulmusKayit.objects.filter(ogrenci_program=op[0])
        assert len(d_kayit) > 0

        # Öğrencinin rolü değiştirilmiş mi?
        arole = AbstractRole.objects.get(name='Lisans Programı Öğrencisi - Kayıt Dondurmuş')
        role = Role.objects.get(user=ogrenci.user)

        assert role.abstract_role.key == arole.key
