# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from time import sleep

import pytest
from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.exceptions import HTTPError


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_authorized_in_menu(self):
        """
        Yetkili kullanıcının menuye erişiminin doğru bir şekilde olup
        olmadığını test eder.

        Sunucuya yapılan request neticesinde
        dönen cevapta `` other, personel, ogrenci, quick_menu, current_user``
        elemanlarının olup olamadığı test edilir ve bu elemanlara ait başka
        elemanlarını olup olmadığı test edilir.

        Veritabanından çekilen kullanıcı bilgileri ile request neticesinde
        sunucudan dönen kullanıcı bilgileri karşılaştırılır.

        """
        usr = User.objects.get(username='personel_isleri_1')
        # '/menu' yolunu çağırır.
        self.prepare_client('/menu', user=usr)
        resp = self.client.post()
        resp.raw()
        # Kullanıcıya izinler ekler.
        self.client.user.role_set[0].role.add_permission_by_name('Atama', True)
        self.client.user.role_set[0].role.add_permission_by_name('Borc', True)
        sleep(1)
        # Kullanıcının izin değişikliklerini görmesi için çıkış yaptırılır.
        self.client.set_path('/logout')
        self.client.post()

        # Yeni kullanıcı yaratmadan, varolan kullanıcıya direkt login yaptırılır.
        self.prepare_client('/menu', user=usr, login=True)
        resp = self.client.post()
        resp.raw()
        lst = ['other', 'personel', 'ogrenci', 'quick_menu', 'current_user']

        # lst elemanlarını, sunucudan dönen cevapta var olup olmadığını test eder.
        assert set(lst).issubset(resp.json.keys())

        for key in lst:
            for value in resp.json[key]:
                try:
                    assert set(value.keys()).issubset(
                        {'kategori', 'param', 'text', 'url', 'wf', 'model'})
                except AttributeError:
                    assert value in ['username', 'surname', 'name', 'roles', 'is_staff', 'role',
                                     'avatar',
                                     'is_student'], 'The %s is not in the given list ' % value

        # Kullanıcı adı baz alınarak veritabanından kullanıcı seçilir.
        usr = User.objects.get(username='personel_isleri_1')

        # Kullanıcının bilgilerini, sunucudan dönen kullanıcı bilgileriyle
        # eşleşip eşleşmediğini test eder.
        assert resp.json['current_user']['name'] == usr.name
        assert resp.json['current_user']['surname'] == usr.surname
        assert resp.json['current_user']['username'] == usr.username

    def test_unauthorized_in_menu(self):
        """
        Yetkili olmayan kullanıcının menu'ye erişememe durumunu test eder.
        Yetkili olmayan kişi menu'ye erişmek istediğinde beklenen
        HTTPUnauthorized hatasını yükseltir.

        """

        # Kullanıcıya çıkış yaptırılır.
        self.client.set_path('/logout')
        # Sunucuya request yapılır.
        self.client.post()

        # Yetkili olmayan kişi menu'ye erişmek istediğinde beklenen
        # HTTPUnauthorized hatasını yükseltir.
        with pytest.raises(HTTPError):
            self.prepare_client('/menu')
            self.client.post()
