# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from .base_test_case import BaseTestCase
from ulakbus.models import AkademikTakvim


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_edit_with_Akademik_Takvim_model(self):
        """
        Akademik Takvim modelini düzenleme işlemi ile test eder.

        """

        # crud iş akışı başlatılır.
        self.prepare_client('/crud')

        # AkademikTakvim modeli ve varsayılan komut 'list' ile sunucuya request yapılır.
        resp = self.client.post(model='AkademikTakvim')
        assert 'objects' in resp.json

        # İlk kaydı düzenlemek için seçer.
        response = self.client.post(model='AkademikTakvim',
                                    cmd='add_edit_form',
                                    object_id=resp.json['objects'][1]['key'])

        object_key = response.json['forms']['model']['object_key']
        unit_id = response.json['forms']['model']['birim_id']

        resp = self.client.post(model='Unit',
                                cmd='object_name',
                                object_id=unit_id)

        objct = AkademikTakvim.objects.get(object_key)
        assert objct.birim.name in resp.json['object_name']

        # Queryset alanına rastgele girilir.
        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='jsghgahfsghfaghfhga')

        # 0 değeri ise queryset alanına girilen değere ait herhangi bir kayıt bulunamadığını gösterir.
        assert resp.json['objects'][0] == 0

        resp = self.client.post(model='Unit',
                                cmd='select_list')

        # -1 değeri ise queryset alanına herhangi bir değer girilmediğini gösterir.
        assert resp.json['objects'][0] == -1

        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='Bilgisayar')

        # Queryset alanına girilen değere ait bir ya da birden fazla kayıt bulunduğunu gösterir.
        assert resp.json['objects'][0] != 0
