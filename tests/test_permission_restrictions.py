# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, Permission, PermissionsRestrictions
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_restrict_permission(self):
        """
        Yetki kisitlamasini test eder.

        """

        PermissionsRestrictions.objects._clear()

        # Veritabanından personel_isleri_1 kullanıcısı seçilir.
        user = User.objects.get(username='personel_isleri_1')

        # Kullanıcın sahip olduğu izinler.
        role = user.role_user_set[0].role
        permissions = role.get_db_permissions()

        number_of_initial_perm = len(permissions)

        restricted_perm = PermissionsRestrictions(
            allow_or_ban=False,
            role_code=role.key,
            permission_code=Permission.objects.get(permissions[0]).key
        )

        # yeni bir kisitlama kurali ekle
        restricted_perm.blocking_save()
        assert number_of_initial_perm == len(role.get_db_permissions()) + 1

        # kurali izinli hale getir
        restricted_perm.allow_or_ban = True
        restricted_perm.blocking_save()
        assert number_of_initial_perm == len(role.get_db_permissions())

        # kurali sil
        restricted_perm.blocking_delete()
        assert number_of_initial_perm == len(role.get_db_permissions())

        # kullanicinin rolu veya abstract roluyle ilgili olmayan bir kural ekle
        new_perm = Permission.objects.get('Okutman.list')
        restricted_perm = PermissionsRestrictions(
            allow_or_ban=True,
            role_code=role.key,
            permission_code=new_perm.key
        )
        # yeni bir kisitlama kurali ekle
        restricted_perm.blocking_save()
        assert number_of_initial_perm == len(role.get_db_permissions()) - 1

        # clear test data
        PermissionsRestrictions.objects._clear()
