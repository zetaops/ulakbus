# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from .base_test_case import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_add_delete_edit_with_hizmet_unvan_model(self):
        """
        HizmetUnvan modelini ekleme, silme ve düzenleme işlemleri ile test eder.

        """

        def len_1(lst):
            """
            Args:
                lst (list): Kayıt nesneleri

            Returns:
                int : Kayıtların sayısı

            """

            return len(lst) - 1

        # crud is akışını başlatır.
        self.prepare_client('/crud')

        # HizmetUnvan modeli ve varsayılan komut 'list' ile sunucuya request yapılır.
        resp = self.client.post(model='HizmetUnvan')
        assert 'objects' in resp.json
        num_of_objects = len_1(resp.json['objects'])

        # İlk kaydı siler, kayıtların listesini döndürür.
        # Silme işlemi için object_id gereklidir.
        self.client.post(model='HizmetUnvan',
                         cmd='delete',
                         object_id=resp.json['objects'][1]['key'])
        resp = self.client.post(model='HizmetUnvan')
        # Kaydın silinip silinmediğini kontrol eder.
        assert num_of_objects - 1 == len_1(resp.json['objects'])
        # Silme işleminin tamamlanmasını bekler.
        time.sleep(1)

        # Yeni kayıt ekler, kayıtların listesi döner.
        self.client.post(model='HizmetUnvan', cmd='add_edit_form')
        resp = self.client.post(model='HizmetUnvan',
                                cmd='save::list',
                                form=dict(tckn="12323121443"))

        assert num_of_objects == len_1(resp.json['objects'])
        # Ekleme işleminin tamamlanmasını bekler.
        time.sleep(1)

        # İlk kaydı düzenlemek için seçer.
        # Düzenleme işlemi için object_id gereklidir.
        resp = self.client.post(model='HizmetUnvan',
                                cmd='add_edit_form',
                                object_id=resp.json['objects'][1]['key'])
        form_data = resp.json['forms']['model']
        form_token = self.client.token
        self.client.token = ''
        resp = self.client.post(model='Personel',
                                cmd='select_list',
                                query='mahmut')
        personel_key, personel_ad = resp.json['objects'][0]['key'], resp.json['objects'][0]['value']
        self.client.token = form_token
        form_data['personel_id'] = personel_key
        # Tarih formatına uygun tarihler atanır.
        form_data['kurum_onay_tarihi'] = '12.09.2011'
        form_data['unvan_bitis_tarihi'] = '11.03.2010'
        form_data['unvan_tarihi'] = '09.04.2909'
        resp = self.client.post(model='HizmetUnvan', cmd='save::list', form=form_data)
        # Düzenleme işleminin tamamlanması bekler.
        time.sleep(1)
        assert num_of_objects == len_1(resp.json['objects'])
        # Mevcut kayıtların sayısının, başlangıçtaki kayıt sayısına eşit olup olmadığını test eder.
