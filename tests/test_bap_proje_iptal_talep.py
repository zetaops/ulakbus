# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from time import sleep

from ulakbus.models import BAPProje
from ulakbus.models import User
from ulakbus.models import Okutman
from ulakbus.models import Personel

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def lane_change_massage_kontrol(self, resp):
        assert resp.json['msgbox']['title'] == 'Teşekkürler!'
        assert resp.json['msgbox']['msg'] == 'Bu iş akışında şuan için gerekli adımları ' \
                                             'tamamladınız. İlgili kişiler, iş akışına ' \
                                             'katılmaları için haberdar edildiler.'

    def test_bap_proje_basvuru(self):
        user = User.objects.get(username='ogretim_uyesi_1')
        personel = Personel.objects.get(user=user)
        okutman = Okutman.objects.get(personel=personel)  # Hanife Şener

        proje = BAPProje()
        proje.ad = "Bap Test proje iptal talebi projesi"
        proje.yurutucu = okutman
        proje.durum = 5
        proje.save()

        for i in range(4):
            if i == 1:
                token, user = self.get_user_token(username='ogretim_uyesi_1')
                self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)
                resp = self.client.post()

                assert resp.json['forms']['form'][0]['helpvalue'] == "%s projeniz için " \
                                                                     "bulunduğunuz iptal talebi " \
                                                                     "reddedilmiştir. " \
                                                                     "Red Açıklaması: Red edildi." \
                                                                     % proje.ad
                self.client.post(form={'bitir': 1})
                sleep(1)
                continue
            elif i == 3:
                token, user = self.get_user_token(username='ogretim_uyesi_1')
                self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)
                resp = self.client.post()

                assert resp.json['forms']['form'][0]['helpvalue'] == "%s projeniz için " \
                                                                     "bulunduğunuz iptal talebi " \
                                                                     "koordinasyon birimi " \
                                                                     "tarafından kabul edilip " \
                                                                     "Komisyon Gündemine " \
                                                                     "alınmıştır." % proje.ad

                self.client.post(form={'bitir': 1})
                sleep(1)
                continue
            else:
                self.prepare_client('/bap_proje_iptal_talep', user=user)

            self.client.post()

            resp = self.client.post(form={'proje': proje.key,
                                          'ilerle': 1})

            assert resp.json['object'][u'Proje Adı'] == proje.ad

            resp = self.client.post(form={'aciklama': 'Kişisel sebeblerden dolayı '
                                                      'bap test projesinin iptalini istiyorum.',
                                          'onay': 1})

            assert resp.json['forms']['form'][0]['helpvalue'] == "%s projesini iptal için onaya " \
                                                                 "yollayacaksınız. Yollamak " \
                                                                 "istiyor musunuz ?" % proje.ad

            resp = self.client.post(form={'gonder': 1})

            self.lane_change_massage_kontrol(resp)

            sleep(1)

            token, user = self.get_user_token(username='bap_koordinasyon_birimi_1')
            self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)

            resp = self.client.post()

            assert resp.json['object']['İptal Talep Açıklama'] == "Kişisel sebeblerden dolayı " \
                                                                  "bap test projesinin " \
                                                                  "iptalini istiyorum."

            if i == 0:
                self.client.post(form={'reddet': 1})

                resp = self.client.post(form={'red_aciklama': 'Red edildi.',
                                              'red_gonder': 1})
            else:
                resp = self.client.post(cmd='onayla', form={'onayla': 1}, object_key=proje.key)
                assert resp.json['forms']['schema']['title'] == "Proje İptal Talebi Talebini " \
                                                                "Komisyona Yolla"
                resp = self.client.post(form={'komisyona_gonder': 1})

            self.lane_change_massage_kontrol(resp)
