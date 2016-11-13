# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_rol_degistir(self):
        for i in range(2):
            # ders_programi_koordinatoru_1 kullanıcısıyla giriş yapılır.
            user = User.objects.get(username='ders_programi_koordinatoru_1')
            # İlk döngüde kullanıcının son login olduğu rol keyi None yapılır.
            if i == 0:
                user.last_login_role_key = None
                user.save()
            # Rol değiştirme iş akışı başlatılır.
            self.prepare_client('/role_switching', user=user)
            resp = self.client.post()
            # İkinci döngüde eğer kullanıcının son login olduğu rolü
            # varsa onunla giriş yapıldığı kontrol edilir.
            if i == 1:
                last_login_role = user.last_login_role()
                assert last_login_role == self.client.current.role
            # Current rol alınır.
            current_role = self.client.current.role
            # Rol seçme ekranında olunduğu kontrol edilir.
            assert 'Switch Role' == resp.json['forms']['schema']["title"]
            # Seçme ekranında bulunan roller bir listeye koyulur.
            role_list = []
            for role in resp.json['forms']['model']["RoleList"]:
                role_list.append(role['key'])
            # Rol seçme seçeneklerinin arasında kullanıcının rolü olmadığı kontrol edilir.
            assert current_role.key not in role_list
            # Ekrandaki rol seçme seçeneklerinin kullanıcının toplam rol sayısından
            # bir eksik olduğu kontrol edilir. (Kendi rolü seçenekler arasında olmadığı
            # için)
            assert len(self.client.user.role_set) == len(
                resp.json['forms']['model']["RoleList"]) + 1
            # Değiştirilecek rol seçilir.
            resp.json['forms']['model']["RoleList"][0]['choice'] = True
            self.client.post(form={'switch': 1})
            # Current rolün değiştiği kontrol edilir.
            assert current_role != self.client.current.role
            # Current rolün seçilen rol olduğu kontrol edilir.
            assert self.client.current.role.key == resp.json['forms']['model']["RoleList"][0]['key']
            # Kullanıcı veritabanından tekrar çekilir.
            user = User.objects.get(username='ders_programi_koordinatoru_1')
            # Kullanıcının last_login_role_key field'ının boş olmadığı kontrol edilir.
            assert user.last_login_role_key != None
            # Kullanıcının last_login_role_key field'ına seçilen rolün atandığı kontrol edilir.
            assert user.last_login_role_key == resp.json['forms']['model']["RoleList"][0]['key']
            # Kullanıcının last_login rolü getirilir.
            new_last_login_role = user.last_login_role()
            # Login rolü ile current rolünün aynı olduğu kontrol edilir.
            assert new_last_login_role == self.client.current.role
            # İş akışı tekrardan başlatılır.
            self.prepare_client('/role_switching', user=user)
            # Current rolün en son değişiklik yapılan rolü olduğu kontrol edilir.
            assert new_last_login_role == self.client.current.role
