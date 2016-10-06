# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import Personel
from zengine.lib.test_utils import *
from zengine.models import Message
import time

__author__ = 'Mithat Raşit Özçıkrıkcı'


class TestCase(BaseTestCase):
    def test_tekil_personel(self):
        """
            Tekil personel terfi (Kanunla verilen terfi) için hazırlanmış test metodudur.
        """

        # Notification kontrolü yapabilmek için öncelikle tüm notificationlar temizlenir.
        Message.objects.delete()
        # Akademik personel seçilir.
        akademik_personel = Personel.objects.get("XFLlsTdqyOV07kgQCbJiIGIvC0v")

        # Personel İşleri Dairesi kullanıcı girişi yapar.
        personel_isleri_usr = User.objects.get(username='personel_isleri_1')
        self.prepare_client('/tekil_personel_terfi', user=personel_isleri_usr)
        resp = self.client.post(id=akademik_personel.key, model="Personel", param="personel_id",
                                wf="tekil_personel_terfi")

        resp = self.client.post(cmd='kaydet', form=resp.json['forms']['model'])
        assert resp.json['msgbox']['title'] == 'İşlem Gerçekleştirildi!'
        time.sleep(1)

        assert Message.objects.count() == 1

        token, user = self.get_user_token("rektor")
        self.prepare_client('/tekil_personel_terfi', user=user, token=token)
        resp = self.client.post()
        # Notification kontrolü yapabilmek için öncelikle tüm notificationlar temizlenir.
        Message.objects.delete()

        resp = self.client.post(cmd="terfi_onay", form=resp.json['forms']['model'])

        assert resp.json['msgbox']['title'] == "TERFİ İŞLEMİ SONUÇ BİLGİSİ"

        time.sleep(1)
        assert Message.objects.count() == 1
        token, user = self.get_user_token("personel_isleri_1")
        self.prepare_client('/tekil_personel_terfi', user=user, token=token)
        self.client.post()
        resp = self.client.post(form={'evet': 1, 'hayir': 'null'})
        assert resp.json['msgbox']['title'] == "TERFİ İŞLEMİ SONUÇ BİLGİSİ"

        # Notification kontrolü yapabilmek için öncelikle tüm notificationlar temizlenir.
        Message.objects.delete()

        idari_personel = Personel.objects.get("UIq8We6bYsj0zXHmnwkLDUDgWWt")

        # Personel İşleri Dairesi kullanıcı girişi yapar.
        personel_isleri_usr = User.objects.get(username='personel_isleri_1')
        self.prepare_client('/tekil_personel_terfi', user=personel_isleri_usr)
        resp = self.client.post(id=idari_personel.key, model="Personel", param="personel_id",
                                wf="tekil_personel_terfi")

        resp = self.client.post(cmd='kaydet', form=resp.json['forms']['model'])
        assert resp.json['msgbox']['title'] == 'İşlem Gerçekleştirildi!'

        time.sleep(1)
        assert Message.objects.count() == 1
        # Genel Sekreter kullanıcıs giriş yapar.
        token, user = self.get_user_token("genel_sekreter_1")
        self.prepare_client('/tekil_personel_terfi', user=user, token=token)
        resp = self.client.post()
        # Notification kontrolü yapabilmek için öncelikle tüm notificationlar temizlenir.
        Message.objects.delete()

        self.client.post(cmd="terfi_red", form=resp.json['forms']['model'])

        resp = self.client.post(form={'devam': 1, 'red_aciklama': "Terfi İşlemi Reddildi"})

        assert resp.json['msgbox']['msg'] == "Terfi işlemi reddedildi"

        time.sleep(1)
        assert Message.objects.count() == 1

        token, user = self.get_user_token("personel_isleri_1")
        self.prepare_client('/tekil_personel_terfi', user=user, token=token)
        resp = self.client.post()
        assert resp.json['msgbox']['type'] == "error"


