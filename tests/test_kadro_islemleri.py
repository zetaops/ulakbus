# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.manage import FlushDB, LoadData
from zengine.lib.test_utils import *
import os
import time
from ulakbus.models import Kadro


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_setup(self):
        """
        Kadro işlemleri iş akışı test edilmeden önce aşağıda
        tanımlı ön hazırlıklar yapılır.

        """

        import sys
        if '-k-nosetup' in sys.argv:
            return

        # Bütün kayıtları veritabanından siler.
        FlushDB(model='all').run()
        # Belirtilen dosyadaki kayıtları ekler.
        LoadData(path=os.path.join(os.path.expanduser('~'), 'ulakbus/tests/fixtures/kadro_islemleri.csv')).run()

    def test_kadro_islemleri(self):
        """
        Kadro işlemleri iş akışını test eder.

        """

        # Veritabanından kullanıcı kaydı seçer.
        usr = User(super_context).objects.get('H7FtslSEbJZAKVvSfU1tZ1nxCfc')
        # Kullanıcıya login yaptırılır.
        self.prepare_client('/kadro_islemleri', user=usr)
        self.client.post()

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('ZRcoPhWHe4u6Rh3BYu1dL9jkTfR')
        # Kadro kaydı seçme işleminin tamamlanmasını bekler.
        time.sleep(1)

        # Seçilen kadronun ilk durumu.
        beginning_state = kadro.get_durum_display()

        # Kadronun durumunu değiştirir. Saklı ise İzinli, İzinli ise Saklı yapar.
        resp = self.client.post(cmd='sakli_izinli_degistir',
                                object_id='ZRcoPhWHe4u6Rh3BYu1dL9jkTfR')

        # Veritabanından kadro kaydı seçer.
        kadro = Kadro.objects.get('ZRcoPhWHe4u6Rh3BYu1dL9jkTfR')
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

        # Duruma göre yapılan filtrelemenin doğruluğunu bütün kayıt durumlarında test eder.
        for i in range(1, len(resp.json['objects'])):
            kadro_key = resp.json['objects'][i]['key']
            kadro = Kadro.objects.get(kadro_key)
            assert kadro.get_durum_display() == 'Saklı'

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
        self.client.token = ''
        resp = self.client.post()
        assert 'list_filters' in resp.json
