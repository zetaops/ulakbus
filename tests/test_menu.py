# -*-  coding: utf-8 -*-
"""

"""
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep
from .base_test_case import BaseTestCase
import pytest
import falcon


class TestCase(BaseTestCase):
    def test_authorized_in_menu(self):
        self.prepare_client('/menu')
        resp = self.client.post()
        resp.raw()
        # Kullaniciya izinler ekliyor
        self.client.user.role_set[0].role.add_permission_by_name('Atama', True)
        self.client.user.role_set[0].role.add_permission_by_name('Borc', True)
        sleep(1)
        # Kullanicinin izin desgisikliklerini gormesi icin cikis yapmasi gerekiyor
        self.client.set_path('/logout')
        self.client.post()
        # Login'e true atayip varolan kullaniciyi direkt login yaptiriyoruz.
        self.prepare_client('/menu', login=True)
        resp = self.client.post()
        resp.raw()
        # Ciktinin asagida tanimlanmis keylere sahip olup olmadigini kontrol ediyor
        assert 'other' and 'personel' and 'ogrenci' in resp.json.keys()
        lst = ['other', 'personel', 'ogrenci']
        for key in lst:

            for value in resp.json[key]:
                # assert sorted(list(value.keys())) == sorted(['kategori', 'param',
                #                                        'text', 'url', 'wf'])
                assert value['url'] in ["crud/Borc", "/yeni_personel", "crud/HizmetBorclanma",
                                        "crud/Atama"]

    def test_unauthorized_in_menu(self):
        self.client.set_path('/logout')
        self.client.post()
        with pytest.raises(falcon.errors.HTTPUnauthorized):
            self.prepare_client('/menu')
            self.client.post()
