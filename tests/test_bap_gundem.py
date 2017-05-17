# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPGundem, BAPProje, User, Personel

from zengine.models import Message
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_gundem(self):
        usr = User.objects.get(username='ogretim_uyesi_1')
        personel = Personel.objects.get(user=usr)

        proje = BAPProje()
        proje.ad = "Test Bap Gündem Proje"
        proje.yurutucu = personel
        proje.save()

        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 2
        gundem.save()

        self.prepare_client('/bap_gundem', username="bap_koordinasyon_birimi_1")
        self.client.post()

        resp = self.client.post(wf='bap_gundem', object_id=gundem.key, cmd='add_edit_form')

        assert resp.json['forms']['model']['object_key'] == gundem.key

        self.client.post(form={'karar_no': 2,
                               'karar': 'Reddedildi',
                               'karar_tarihi': '21.04.2017',
                               'kaydet': 1,
                               'model_type': 'BAPGundem',
                               'object_key': gundem.key,
                               'oturum_numarasi': 5,
                               'oturum_tarihi': '21.04.2017'},
                         cmd='save')
        self.client.post()

        resp = self.client.post(wf='bap_gundem', object_id=gundem.key, cmd='show')

        show_data = {u'Gündem Tipi': 'Ek bütçe talebi',
                     u'Karar': 'Reddedildi',
                     u'Karar No': '2',
                     u'Karar Tarihi': '21.04.2017',
                     u'Kararın Sonuçlandırılması': 'Sonuçlandı',
                     u'Oturum Numarası': '5',
                     u'Oturum Tarihi': '21.04.2017'}

        for key, value in show_data.items():
            assert resp.json['object'][key] == value

        assert resp.json['object_key'] == gundem.key

        self.client.post(form={'tamam': 1}, object_key=gundem.key)

        time.sleep(1)

        sender_user = User.objects.get(username='bap_koordinasyon_birimi_1')

        message = Message.objects.get(sender=sender_user, receiver=usr,
                                      msg_title='Komisyon Kararı')

        assert message.body == 'Test Bap Gündem Proje adlı projenizin' \
                               ' Ek bütçe talebi komisyon kararı ' \
                               'Karar: Reddedildi'

        message.delete()
        proje.delete()
        gundem.delete()
