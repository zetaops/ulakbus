# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPGundem, BAPProje, Personel, User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def lane_change_massage_kontrol(self, resp):
        assert resp.json['msgbox']['title'] == 'Teşekkürler!'
        assert resp.json['msgbox']['msg'] == 'Bu iş akışında şuan için gerekli adımları ' \
                                             'tamamladınız. İlgili kişiler, iş akışına ' \
                                             'katılmaları için haberdar edildiler.'

    def test_bap_ek_sure_talep(self):
        proje = BAPProje()
        user = User.objects.get(username='ogretim_uyesi_1')
        personel = Personel.objects.get(user=user)
        proje.ad = "Test ek süre talep projesi"
        proje.yurutucu = personel
        proje.save()

        talep_form = {'ek_sure': 3,
                              'aciklama': 'Test ek süre talep açıklaması',
                              'gonder': 1,
                              'proje': proje.key}

        for i in range(3):
            time.sleep(1)
            if i == 0:
                self.prepare_client('/bap_ek_sure_talep', user=user)
            else:
                token, user = self.get_user_token('ogretim_uyesi_1')
                self.prepare_client('/bap_ek_sure_talep', user=user, token=token)

            resp = self.client.post()

            if i == 1:
                assert resp.json['msgbox']['title'] == 'Talebiniz Reddedildi.'
                assert resp.json['msgbox']['msg'] == 'Reddedildi'
                talep_form['ek_sure'] = 2
            if i == 2:
                assert resp.json['msgbox']['title'] == 'Talebiniz Kabul Edildi.'
                assert resp.json['msgbox']['msg'] == 'Ek süre için bulunduğunuz talep ' \
                                                     'kabul edilmiş olup, komisyonun ' \
                                                     'gündemine alınmıştır.'
                break

            resp = self.client.post(wf='bap_ek_sure_talep', form=talep_form)
            self.lane_change_massage_kontrol(resp)

            time.sleep(1)

            token, user = self.get_user_token(username='bap_koordinasyon_birimi_1')
            self.prepare_client('/bap_ek_sure_talep', user=user,
                                token=token)
            resp = self.client.post()
            assert resp.json['object']['Talep Edilen Süre(Ay olarak)'] == str(talep_form['ek_sure'])
            assert resp.json['object']['Açıklama'] == talep_form['aciklama']
            if i == 0:
                resp = self.client.post(form={'reddet': 1}, token=token, cmd='iptal')
                assert resp.json['forms']['schema']['title'] == 'Red Açıklaması Yazınız'

                resp = self.client.post(form={'red_aciklama': 'Reddedildi',
                                              'red_gonder': 1}, token=token, wf='bap_ek_sure_talep')

            if i == 1:
                self.client.post(form={'onayla': 1}, token=token, cmd='kabul')
                resp = self.client.post(form={'komisyon_aciklama': 'Ek süre talebi kontrol '
                                                                   'edildi.',
                                              'yolla': 1})
            self.lane_change_massage_kontrol(resp)

        proje.reload()

        assert proje.durum == 4
        gundem = BAPGundem.objects.all(proje=proje, gundem_tipi=4)
        assert len(gundem) == 1

        proje.delete()
