# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import User

from zengine.lib.test_utils import BaseTestCase
from zengine.models import TaskInvitation
from zengine.models import WFInstance

import time


class TestCase(BaseTestCase):
    def test_etkinlik_basvuru_listele_incele(self):
        user = User.objects.get(username='bap_koordinasyon_birimi_1')

        # Etkinlik basvuru sayisi alinir
        sayi = BAPEtkinlikProje.objects.count()

        # etkinlik basvuru listeleme is akisi baslatilir.
        self.prepare_client('/bap_etkinlik_basvuru_listele', user=user)
        resp = self.client.post()

        assert len(resp.json['objects']) == sayi + 1

        resp = self.client.post(cmd='goruntule', object_id='Yt4VkZQfnt9XEiSnMcZvUKUWSj')

        assert resp.json[
                   'object_title'] == 'Bilimsel Etkinliklere Katılım Desteği : ' \
                                      'Çay Yaprağı Paradoksunda Akışkanlar Mekaniğinin Yeri ' \
                                      '| Henife Şener'

        resp = self.client.post(cmd='komisyon')

        assert 'msgbox' in resp.json

        token, user = self.get_user_token('bap_komisyon_baskani_1')
        self.prepare_client('/bap_etkinlik_basvuru_incele', user=user, token=token)
        resp = self.client.post()

        assert resp.json[
                   'object_title'] == 'Bilimsel Etkinliklere Katılım Desteği : ' \
                                      'Çay Yaprağı Paradoksunda Akışkanlar Mekaniğinin Yeri ' \
                                      '| Henife Şener'

        resp = self.client.post(cmd='komisyon_uyesi_ata')

        assert resp.json['forms']['schema']['title'] == 'Komisyon Üyesi Seç'

        resp = self.client.post(form={'komisyon_uye': 'TSGpHLAksW29pyFhTUtVvIHMFlI'})

        assert 'msgbox' in resp.json

        wfi = WFInstance.objects.get(token)
        time.sleep(1)
        TaskInvitation.objects.get(instance=wfi).blocking_delete()
        time.sleep(1)
        wfi.blocking_delete()

