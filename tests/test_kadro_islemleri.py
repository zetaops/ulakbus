# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time
from pyoko.model import super_context
from ulakbus.models import Kadro, User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_kadro_islemleri(self):
        """
        Kadro işlemlerinin ilk adımında kayıtlı olan kadroların listesi döner.

        Veritabanından çekilen kadro kayıtlarının sayısı ile sunucudan dönen kadro
        kayıtlarının sayısı karşılastırılıp test edilir.

        Seçilen kadronun, kadro durumu değiştirilir. Bu değişikliğin kayıt edilip
        edilmediği test edilir.

        Seçilen  kadro durumuna göre filtereleme yapılır, yapılan filterelemenin
        doğruluğunu bütün kayıt durumlarında test eder.

        Filterelemenin ardından sunucudan dönen kadro kayıtları sayısı ile db'den
        duruma göre çekilen kadro kayıtlarının sayısı karşılaştılıp test edilir.

        Yeni kayıt eklendikten sonra döndürülen kayıt sayısının, başlangıçtaki kayıt
        sayısından bir fazla olup olmadığın test edilir.

        Sadece saklı kadrolar silinir. Bir kaydı silmek için seçtiğimizde kadro durum

        1 ise;
             Kadro silinir, başlangıçtaki kadro kayıtları sayısı ile silme islemi
             sonucundaki kadro kayıtları sayısı test edilir.

        2,3,4 ise;
             Kadro silinmez, başlangıçtaki kadro kayıtları sayısı ile silme islemi
             sonucundaki kadro kayıtları sayısı test edilir.


        """

        def len_1(lst):
            """
            ``response`` ile gelen ``object`` içerisinde field açıklamaları
            satırı bulunmaktadır. Bu sebeple nesnelerin gerçek sayısını
            bulmak için 1 eksiltiyoruz.

            Args:
                lst (list): kadro nesneleri listesi

            Returns:
                int: lst uzunlugunun 1 eksigi

            """

            return len(lst) - 1

        # Veritabanından personel işleri kullanıcısı seçer.
        usr = User(super_context).objects.get('UuXR8pmKQNzfaPHB2K5wxhC7WDo')

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/kadro_islemleri', user=usr)
        resp = self.client.post()

        # Kayıtlı kadroların listesini veritabanından çeker.
        kadro_lst = Kadro.objects.filter()

        # Sunucudan dönen kadro kayıtlarının sayısı.
        num_of_kadro = len_1(resp.json['objects'])

        assert len(kadro_lst) == num_of_kadro

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('8ICt8g0NpPdn5eDfh4yz0vsLqkn')

        # Seçilen kadronun ilk durumu.
        beginning_state = kadro.get_durum_display()

        # Kadronun durumunu değiştirir. Saklı ise İzinli, İzinli ise Saklı yapar.

        self.client.post(cmd='sakli_izinli_degistir',
                         object_id='8ICt8g0NpPdn5eDfh4yz0vsLqkn')

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('8ICt8g0NpPdn5eDfh4yz0vsLqkn')

        # Kadronun son durumu.
        last_state = kadro.get_durum_display()
        # Saklı izinli değiştir komutundan sonra kadronun durumunu kontrol eder.
        assert beginning_state != last_state

        # durum bir kez daha degistirilir.
        self.client.post(cmd='sakli_izinli_degistir',
                         object_id='8ICt8g0NpPdn5eDfh4yz0vsLqkn')

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('8ICt8g0NpPdn5eDfh4yz0vsLqkn')

        # Kadronun son durumu.
        last_state = kadro.get_durum_display()

        # Ikinci saklı izinli değiştir komutundan sonra kadronun durumunu kontrol eder.
        assert beginning_state == last_state

        # İş akışının başlangıç token değeridir.
        filtre = {'durum': {'values': ["1"], 'type': 'check'}}
        # Seçilen kadro durumuna göre filtreler.
        resp = self.client.post(filters=filtre)
        assert 'list_filters' in resp.json

        # Sunucudan dönen saklı kadro kayıtlarının sayısını tutar.
        num_of_sakli = 0

        # Duruma göre yapılan filtrelemenin doğruluğunu bütün kayıt durumlarında test eder.
        for i in range(1, len(resp.json['objects'])):
            kadro_key = resp.json['objects'][i]['key']
            kadro = Kadro.objects.get(kadro_key)
            assert kadro.get_durum_display() == 'Saklı'
            num_of_sakli += 1

        # Veritabanından çekilen saklı kadro sayısı ile sunucudan dönen saklı
        # kadro sayıları karşılaştırılır.
        assert len(Kadro.objects.filter(durum=1)) == num_of_sakli

        # Crud iş akışı başlatılır.
        self.client.token = ''
        self.client.set_path('/crud')
        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='Halkla')

        birim_no = resp.json['objects'][0]['key']

        # Yeni kadro kaydı ekler.
        self.client.set_path('/kadro_islemleri')
        self.client.post()
        form_token = self.client.token
        resp = self.client.post(cmd='add_edit_form', form=dict(add=1))

        # Kadro ekle formu doldurulur.
        kadro_data = {'unvan': 22469, 'unvan_aciklama': '22464', 'derece': 8, 'birim_id': birim_no,
                      'kadro_no': 4, 'save_edit': 1, 'aciklama': '8.dereceden kadro'}

        # Kadro kaydını kaydeder.
        self.client.post(cmd='kadro_kaydet', form=kadro_data, token=form_token)

        time.sleep(1)
        yeni_kadro = Kadro.objects.get(unvan=22469, unvan_aciklama='22464', derece=8)

        last_kadro_lst = Kadro.objects.filter()

        self.client.set_path('/kadro_islemleri')
        resp = self.client.post()

        assert len(last_kadro_lst) == num_of_kadro + 1
        assert len_1(resp.json['objects']) == len(last_kadro_lst)

        # Seçilen kadronun durumu.
        kadro_durum = yeni_kadro.durum

        # Kadronun durumu saklı ise silinir, değilse silinmez.
        self.client.post(cmd='kadro_sil_onay_form',
                         object_id=yeni_kadro.key)
        resp = self.client.post(cmd='kadro_sil', form={'evet': 1, 'hayir': 'null'})

        kadro_lst = Kadro.objects.filter()

        assert len_1(resp.json['objects']) == len(kadro_lst)

        if kadro_durum not in [1, 2, 3, 4]:
            raise Exception('Geçersiz kadro durumu.')
