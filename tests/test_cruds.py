# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from .base_test_case import BaseTestCase


class TestCase(BaseTestCase):
    """Test Durumu

    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_list_add_delete_with_employee_model(self):
        """
        Personel  modelini listele, ekleme ve silme işlemleri ile test eder.

        """

        def len_1(lst):
            return len(lst) - 1

        # Crud iş akışını başlatır.
        self.prepare_client('/crud')
        # Personel modeli ve varsayılan komut "list" ile sunucuya request yapılır.
        resp = self.client.post(model='Personel')
        assert 'objects' in resp.json
        # Mevcut kayıtların sayısını tutar.
        num_of_objects = len_1(resp.json['objects'])
        # Yeni bir personel kaydı ekler, kayıtların listesini döndürür.
        self.client.post(model='Personel', cmd='add_edit_form')
        resp = self.client.post(model='Personel',
                                cmd='save::list',
                                form=dict(ad="Em1", tckn="12323121443"))
        # Eklenen kaydın, başlangıçtaki kayıtların sayısında değişiklik yapıp yapmadığını test eder.
        assert num_of_objects + 1 == len_1(resp.json['objects'])
        # İlk kaydı siliyor, kayıtların listesini döndürüyor.
        resp = self.client.post(model='Personel',
                                cmd='delete',
                                object_id=resp.json['objects'][1]['key'])
        # Mevcut kayıtların sayısının, başlangıçtaki kayıt sayısına eşit olup olmadığını test eder.
        assert 'reload' in resp.json['client_cmd']

    def test_add_search_filter(self):
        """
        Personel modelini arama, ekleme ve filtreleme işlemleri ile test eder.

        """

        # Crud iş akışını başlatır.
        self.prepare_client('/crud')
        resp = self.client.post(model='Personel')
        # query değerine göre kayıtları filtreler ve response döndürür.
        resp = self.client.post(model='Personel', query="1234567")
        # Kayıtların sayısı 2'den küçükse, yeni kayıtlar ekler.
        if len(resp.json['objects']) < 2:
            self.client.post(model='Personel', cmd='add_edit_form')
            for i in range(9):
                resp = self.client.post(model='Personel',
                                        cmd='save::add_edit_form',
                                        form=dict(ad="Per%s" % i, tckn="123456789%s" % i))
            time.sleep(3)

        resp = self.client.post(model='Personel')
        resp = self.client.post(model='Personel', query="12345678")
        assert len(resp.json['objects']) > 8
