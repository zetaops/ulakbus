# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_ogrenci_ders_ekleme(self):
        user = User.objects.get(username='ogrenci_1')
        self.prepare_client('/ogrenci_ders_ekleme', user=user)
        resp = self.client.post()
        resp = self.client.post(form={'onayla': 1, 'Dersler': resp.json['forms']['model']['Dersler']})
        resp = self.client.post(
            form={'onayla': 1, 'Dersler': resp.json['forms']['model']['Dersler'], 'alttan_ders_sec': 1})
        resp = self.client.post(
            form={'onayla': 1, 'Dersler': resp.json['forms']['model']['Dersler'], 'alttan_ders_sec': 1, 'gdz_sec': 1})
        resp = self.client.post(form={'evet': 'null', 'hayir': 1, 'flow': 'farkli_bolumlerden_ders_sec'})
        resp = self.client.post(
            form={'onayla': 1, 'Dersler': [], 'alttan_ders_sec': 1, 'gdz_sec': 1, 'gdzs_sec':1})
        resp = self.client.post(form={'onayla': 1, 'Dersler': []})
        time.sleep(1)
        token, user = self.get_user_token(username='danisman_1')
        self.prepare_client('/ogrenci_ders_ekleme', user=user, token=token)
        self.client.post()