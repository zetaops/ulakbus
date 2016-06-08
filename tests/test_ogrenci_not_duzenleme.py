# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User, Sinav, OgrenciDersi, DegerlendirmeNot, Sube
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ogrenci_not_duzenleme(self):
        # Veritabanından ogrenci_isleri_1 kullanıcısı seçilir.
        usr = User.objects.get(username='ogrenci_isleri_1')

        # Öğrenci işleri not düzenleme iş akışı başlatılır.
        self.prepare_client('/ogrenci_not_duzenleme', user=usr)
        self.client.post()

        # Fakülte karar no'su girilir.
        resp = self.client.post(form={'karar': 4543, 'kaydet': 1})

        # Sube sayısı.
        len_of_sube = Sube.objects.filter().count()

        # Sunucudan dönen sube sayısı ile veritabanından çekilen sınav sayısı karşılaştırılıp test edilir.
        assert len_of_sube == len(resp.json['forms']['form'][1]['titleMap'])

        # subeler = [{'key': "I8BhWGKroZIp3fp5b26ZtZJTULO", 'ders_adi': "Kuyruk Sistemleri - A101 30"}]
        # resp = self.client.post(form={'ileri': 1, 'form_key': "e35fec7a2b4e4297b2e278a64096d73a", 'Subeler': subeler})
        # Sube seçilir.
        resp = self.client.post(form={'ileri': 1, 'sube': "I8BhWGKroZIp3fp5b26ZtZJTULO"})

        # Şubeye bağlı sınav sayısı
        len_of_sinav = Sinav.objects.filter(sube_id="I8BhWGKroZIp3fp5b26ZtZJTULO").count()

        # Sunucudan dönen sınav sayısı ile veritabanından çekilen sınav sayısı karşılaştırılıp test edilir.
        assert len_of_sinav == len(resp.json['forms']['form'][1]['titleMap'])

        # Sınav seçilir.
        resp = self.client.post(form={'sinav': 'OgBWnRDaAc39gID3aa2yj7VR9rC', 'ileri': 1})

        ogrenciler = [{'ad_soyad': "Salık Durmaz", 'secim': 'true', 'ogrenci_key': "YmbiCB5FR27xeB5IPrD0R8h4UiJ"}]

        ogrenci_lst = []
        # Şubeye kayıtlı öğrenci dersleri.
        ogrenci_dersi_lst = OgrenciDersi.objects.filter(sube_id="I8BhWGKroZIp3fp5b26ZtZJTULO")
        for ogrenci_dersi in ogrenci_dersi_lst:
            ogrenci_lst.append(ogrenci_dersi.ogrenci)

        # Veritabanından dönen öğrenci sayısı ile sunucudan dönen öğrenci sayısı karşılaştırılıp test edilir.
        assert len(resp.json['forms']['model']['Ogrenciler']) == len(ogrenci_lst)

        # Öğrenci seçilir.
        self.client.post(form={'ileri': 1, 'Ogrenciler': ogrenciler})

        assert 'LANE_CHANGE_MSG' in self.client.current.task_data

        # time.sleep(1)
        #
        # token, user = BaseTestCase.get_user_token(username='ogretim_uyesi_1')
        #
        # # ogretim_uyesi_1 kullanıcısına giriş yaptılır.
        # self.prepare_client('/ogrenci_not_duzenleme', user=user, token=token)
        # self.client.post()

        # baslangic_puani = DegerlendirmeNot.objects.get("Xq6MpL4xGFmZKEb7TAaCqIGDmRw").puan
        # self.client.post(form={'kaydet': 1, "object_key": "Xq6MpL4xGFmZKEb7TAaCqIGDmRw", 'puan': 50})
        # son_puani = DegerlendirmeNot.objects.get("Xq6MpL4xGFmZKEb7TAaCqIGDmRw").puan
        # assert baslangic_puani != son_puani and son_puani == 50

