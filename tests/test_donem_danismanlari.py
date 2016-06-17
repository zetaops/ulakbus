# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import DonemDanisman, Donem
from ulakbus.models.auth import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_donem_danismanlari(self):
        """
        Dönem danışmanları iş akışı başlattıktan sonra;

        İş akışının ilk adımında bölüm başkanın kayıtlı olduğu bölüm seçilir.

        Sunucudan dönen bölüme ait dönem danışmanlarının sayısı ile
        veritabanından çekilen dönem danışmanlarının sayısı
        karşılaştırılıp test edilir.

        İş akışının ikinci adımında seçilen danışmanlar kaydedilir.

        Seçilen danışmanlarının  veritabanına kaydedilip edilmediğini kontrol edilir ve
        seçilenen danışmanlar kaydedildikten sonra, sunucudan dönen cevapta danışman
        kayıt sayılarında degişiklik olup olmadığı test edilir.

        """

        # Veritabanından bölüm başkanı kullanıcısı seçilir.
        usr = User.objects.get(username='bolum_baskani_1')

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/donem_danismanlari', user=usr)
        resp = self.client.post()

        # Kullanıcının kayıtlı olduğu bolum seçilir.
        resp = self.client.post(form={'ileri': 1, 'program': "BpmGHdZo8sQC85cL6wffYr4CEKh"})

        # Kullanıcının kayıtlı olduğu bölüm.
        bolum = usr.role_set[0].role.unit

        donem = Donem.objects.get(guncel=True)

        # Db'den varolan danışman  kayıtları seçilir.
        count_of_danisman = len(DonemDanisman.objects.filter(donem=donem, bolum=bolum))
        time.sleep(1)
        num_of_danisman = 0
        for okutman in resp.json['forms']['model']['Okutmanlar']:
            if okutman['secim']:
                num_of_danisman += 1

        # Sunucudan dönen danışman kayıtlarının sayısı ile veritabanından çekilen
        # danışman kayıtlarının sayısının eşitliği karşılşatılırıp test edilir.
        assert num_of_danisman == count_of_danisman

        # 3 tane daha danışman seçilir.
        okutmanlar = [
            {'ad_soyad': "Yalın Seven", 'secim': "true", 'key': "Bf1CPIKs6txfhvlBQ7jqhy0iwv"},
            {'ad_soyad': "Meşhur Ertaş", 'secim': "true", 'key': "O88eWBlnA579TqHs1oYuZITeHsg"},
            {'ad_soyad': "Mengi Bilgin", 'secim': "true", 'key': "180kVRsM8JR7Aql8xVRC9L0L4HW"},
            {'ad_soyad': "Sevla Demirel", 'secim': "", 'key': "8oS60wq2nhZLuZ4Dqsn4YtofPSF"},
            {'ad_soyad': "Uluğbey Bilgin", 'secim': "", 'key': "YhkwdYaGFnVzWMpULy6unvuON1A"},
            {'ad_soyad': "Anka Çorlu", 'secim': "", 'key': "O7M6ndhCp4FhAZiYQHr52IasJSG"},
            {'ad_soyad': "Övün Alemdar", 'secim': "", 'key': "4O7Nxt64EQumUzettWGyPHU9r3C"},
            {'ad_soyad': "Safura Kısakürek", 'secim': "", 'key': "9YivWjZb4iPp2O6eQq1X4bqkfIW"},
            {'ad_soyad': "Veis Güçlü", 'secim': 'true', 'key': "JdH5RzwbmhIBTAU4ec6J4fgNu4z"},
            {'ad_soyad': "Öge Fırat", 'secim': "", 'key': "22Y0VMB98avgMjSbbH1KXkZrdLL"}]

        # Seçilen dönem danışmanları kaydedilir.
        self.client.post(form={'kaydet': 1, 'Okutmanlar': okutmanlar})
        time.sleep(1)

        # Eklenen danışman kayıtlarının veritabanına kaydedilip kaydedilmediğini test eder.
        assert len(DonemDanisman.objects.filter(donem=donem, bolum=bolum)) == count_of_danisman + 3

        # İş akışı tekrardan başlatılır.
        self.client.set_path('/donem_danismanlari')
        resp = self.client.post()

        # Kullanıcının kayıtlı olduğu bolum seçilir.
        resp = self.client.post(form={'ileri': 1, 'program': "BpmGHdZo8sQC85cL6wffYr4CEKh"})

        num_of_danisman = 0
        for okutman in resp.json['forms']['model']['Okutmanlar']:
            if okutman['secim']:
                num_of_danisman += 1

        # Eklenen danışmanlar kaydedildikten sonra, sunucudan dönen cevapta danışman kayıt sayıların
        # doğruluğu test edilir.
        assert num_of_danisman == count_of_danisman + 3

        for dd in DonemDanisman.objects.filter(donem=donem, bolum=bolum):
            if not dd.okutman.key == 'Bf1CPIKs6txfhvlBQ7jqhy0iwv':
                dd.delete()
