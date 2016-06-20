# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import pytest

from ulakbus.models import User, Role, Permission
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.test_utils import HTTPError

PERMISSION_LST = [permission.code for permission in Permission.objects.filter(code__contains='Borc')]


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_authorized_in_menu(self):
        """
        Yetkili kullanıcının menuye erişiminin doğru bir şekilde olup
        olmadığını test eder.

        Sunucuya yapılan request neticesinde
        dönen cevapta `` other, settings, quick_menu, current_user``
        elemanlarının olup olamadığı test edilir.

        Kullanıcıya izinler eklenir, izinlerin eklenip eklenmediği
        test edilir.

        Veritabanından çekilen kullanıcı bilgileri ile request neticesinde
        sunucudan dönen kullanıcı bilgileri karşılaştırılır.

        Hidden davranışına sahip iş akışlarının menu bölümünde bulunmaması gerekir.
        Hidden davranışa sahip Hitap İşlemleri iş akışının menu kısmında olup olmadığı
        test edilir.

        """
        # Veritabanından personel_isleri_1 kullanıcıs seçilir.
        usr = User.objects.get(username='personel_isleri_1')

        # '/menu' yolunu çağırır, kullanıcıya giriş yaptırılır.
        self.prepare_client('/menu', user=usr)
        resp = self.client.post()

        # Kullanıcın sahip olduğu izinler.
        first_permissions = self.client.user.role_set[0].role.get_db_permissions()

        # Kullanıcıya izinler eklenir.
        self.client.user.role_set[0].role.add_permission_by_name('Borc', save=True)

        # Kullanıcıya permisionlar eklendikten sonraki izinleri.
        last_permissions = self.client.user.role_set[0].role.get_db_permissions()

        # İzinlerin eklenip eklenmediği test edilir.
        assert len(last_permissions) == len(first_permissions) + len(PERMISSION_LST)

        # Kullanıcın rolünün keyi.
        user_role_key = self.client.user.role_set[0].role.key
        # Permission değişikliklerini görmek için role çekilir.
        user_role = Role.objects.get(user_role_key)

        # Kullanıcıya eklelen izinler silinir.
        TestCase.delete_added_permissions(user_role=user_role)
        lst = ['settings', 'other', 'current_user', 'quick_menu', 'personel']

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
                                     'is_student', 'static_url'], 'The %s is not in the given list ' % value

        # Kullanıcının bilgilerini, sunucudan dönen kullanıcı bilgileriyle
        # eşleşip eşleşmediğini test eder.
        assert resp.json['current_user']['name'] == usr.name
        assert resp.json['current_user']['surname'] == usr.surname
        assert resp.json['current_user']['username'] == usr.username

        # Hizmet Cetveli iş akışının hidden özeliği test edilir.
        for response in resp.json['other']:
            assert response['text'] != 'Hizmet Cetveli'

    @staticmethod
    def delete_added_permissions(user_role):
        """
        Kullanıcıya eklenen izinler silinir.

        Args:
            user_role : Kullanıcı nesnesi

        Returns:
            delete_added_permissions fonksiyonunu

        """
        for permission in user_role.Permissions:
            if permission.permission.code in PERMISSION_LST:
                permission.remove()
                user_role.save()
                return TestCase.delete_added_permissions(user_role)

    def test_unauthorized_in_menu(self):
        """
        Yetkili olmayan kullanıcının menu'ye erişememe durumunu test eder.
        Yetkili olmayan kişi menu'ye erişmek istediğinde beklenen
        HTTPUnauthorized hatasını yükseltir.

        """

        # Kullanıcıya çıkış yaptırılır.
        self.client.set_path('/logout')
        self.client.post()

        # Yetkili olmayan kişi menu'ye erişmek istediğinde beklenen
        # HTTPUnauthorized hatasını yükseltir.
        with pytest.raises(HTTPError):
            self.prepare_client('/menu')
            self.client.post()
