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
            Args:
                objects (list): Kadro nesneleri

            Returns:
                Kadro kayıtlarının sayısını

            """

            return len(lst) - 1

        # Veritabanından kullanıcı kaydı seçer.
        usr = User(super_context).objects.get('H7FtslSEbJZAKVvSfU1tZ1nxCfc')

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/kadro_islemleri', user=usr)
        resp = self.client.post()

        # Kayıtlı kadroların listesini veritabanından çeker.
        kadro_lst = Kadro.objects.filter()

        # Sunucudan dönen kadro kayıtlarının sayısı.
        num_of_kadro = len_1(resp.json['objects'])

        assert len(kadro_lst) == num_of_kadro

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('IEinP7MulDERqiP1cB4QDB2If45')
        # Kadro kaydı seçme işleminin tamamlanmasını bekler.
        time.sleep(1)

        # Seçilen kadronun ilk durumu.
        beginning_state = kadro.get_durum_display()

        # Kadronun durumunu değiştirir. Saklı ise İzinli, İzinli ise Saklı yapar.
        resp = self.client.post(cmd='sakli_izinli_degistir',
                                object_id='IEinP7MulDERqiP1cB4QDB2If45')

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('IEinP7MulDERqiP1cB4QDB2If45')
        # Kadro kaydı seçme işleminin tamamlanmasını bekler.
        time.sleep(1)

        # Kadronun son durumu.
        last_state = kadro.get_durum_display()
        # Saklı izinli değiştir komutundan sonra kadronun durumunu kontrol eder.
        assert beginning_state != last_state

        # İş akışının başlangıç token değeridir.
        form_token = self.client.token

        filter = {'durum': {'values': ["1"], 'type': 'check'}}
        # Seçilen kadro durumuna göre filtreler.
        resp = self.client.post(filters=filter)

        # Filtreleme yapılırken token değiştiği için başlangıç token değeri atanır.
        self.client.token = form_token

        # Sunucudan dönen saklı kadro kayıtlarının sayısını tutar.
        num_of_sakli = 0

        # Duruma göre yapılan filtrelemenin doğruluğunu bütün kayıt durumlarında test eder.
        for i in range(1, len(resp.json['objects'])):
            kadro_key = resp.json['objects'][i]['key']
            kadro = Kadro.objects.get(kadro_key)
            assert kadro.get_durum_display() == 'Saklı'
            num_of_sakli += 1

        # Veritabanından çekilen saklı kadro sayısı ile sunucudan dönen saklı kadro sayıları karşılaştırılır.
        assert len(Kadro.objects.filter(durum=1)) == num_of_sakli

        # Yeni kadro kaydı ekler.
        self.client.post(cmd='add_edit_form',
                         form=dict(add=1))

        # Yeni bir iş akışı başlatılacağı için token değeri sıfırlanır.
        self.client.token = ''

        # Crud iş akışı başlatılır.
        self.client.set_path('/crud')
        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='Halkla')

        birim_no = resp.json['objects'][0]['key']

        # Kadro ekle formu doldurulur.
        kadro_data = {'unvan': 3, 'unvan_kod': 22464, 'derece': 3, 'birim_id': birim_no,
                      'kadro_no': 4, 'save_edit': 1,
                      'aciklama': 'kadro'}

        self.client.set_path('/kadro_islemleri', token=form_token)
        # Kadro kaydını kaydeder.
        resp = self.client.post(form=kadro_data)
        assert 'reset' in resp.json['client_cmd']

        # İş akışı resetlendiği için token değeri sıfırlanıyor.
        self.client.set_path('/kadro_islemleri')
        resp = self.client.post()
        assert 'list_filters' in resp.json

        assert len(resp.json['objects']) == len(kadro_lst) + 1

        # Kadro nesnesi seçilir.
        kadro_object = Kadro.objects.get('IEinP7MulDERqiP1cB4QDB2If45')
        # Seçilen kadronun durumu.
        kadro_durum = kadro_object.durum

        # Kadronun durumu saklı ise silinir, değilse silinmez.
        self.client.post(cmd='kadro_sil_onay_form',
                                object_id='IEinP7MulDERqiP1cB4QDB2If45')
        resp = self.client.post(cmd='kadro_sil', form={'evet': 1, 'hayir': 'null'})
        time.sleep(1)

        if kadro_durum == 1:
            # Yukarıda kadro eklendiği için ve silme islemi gerçekleştiği
            # için len(kadro_lst) değişmez.
            assert len(kadro_lst) == len_1(resp.json['objects'])
        elif kadro_durum in [2, 3, 4]:
            assert len(resp.json['objects']) == len(kadro_lst) + 1
        else:
            raise Exception('Geçersiz kadro durumu.')
