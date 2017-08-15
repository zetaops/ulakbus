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
        yeni_okutman = Okutman.objects.get('I1QVJUVQ2FydxNsxksJCXn9cdeT')  # İsmet Tarhan

        proje = BAPProje()
        proje.ad = "Bap Test yürütücü değişikliği projesi"
        proje.yurutucu = okutman
        proje.durum = 5
        proje.save()

        for i in range(4):

            if i == 1:
                token, user = self.get_user_token(username='ogretim_uyesi_1')
                self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)
                resp = self.client.post()

                assert resp.json['forms']['form'][0]['helpvalue'] == "%s projeniz için %s " \
                                                                     "'in yerine %s 'in yürütücü" \
                                                                     " olarak atanması talebiniz " \
                                                                     "reddedilmiştir. " \
                                                                     "Red Açıklaması: Red " \
                                                                     "edildi." % (proje.ad,
                                                                                  okutman,
                                                                                  yeni_okutman)
                self.client.post(form={'bitir': 1})
                sleep(1)
                continue
            elif i == 3:
                token, user = self.get_user_token(username='ogretim_uyesi_1')
                self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)
                resp = self.client.post()

                assert resp.json['forms']['form'][0]['helpvalue'] == "%s projeniz için %s " \
                                                                     "'in yerine %s 'in " \
                                                                     "yürütücü olarak atanması " \
                                                                     "talebiniz koordinasyon " \
                                                                     "birimi tarafından kabul " \
                                                                     "edilip Komisyon Gündemine " \
                                                                     "alınmıştır." % (
                    proje.ad, okutman, yeni_okutman)

                self.client.post(form={'bitir': 1})
                sleep(1)
                continue
            else:
                self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user)

            self.client.post()

            resp = self.client.post(form={'proje': proje.key,
                                          'ilerle': 1})

            assert resp.json['forms']['schema']['title'] == 'Yürütücü Değişikliği Talebi'

            resp = self.client.post(form={'yurutucu_id': yeni_okutman.key,
                                          'aciklama': 'Yeni yurutucu İsmet Tarhan olmasını istiyorum',
                                          'ilerle': 1})

            assert resp.json['forms']['form'][0]['helpvalue'] == "%s projesinin mevcut yürütücüsü " \
                                                                 "olan %s 'nın yerine %s 'nın " \
                                                                 "yürütücü olarak atanması " \
                                                                 "talebinde bulunuyorsunuz." % (
                proje.ad, okutman, yeni_okutman)

            resp = self.client.post(form={'gonder': 1})

            self.lane_change_massage_kontrol(resp)

            sleep(1)

            token, user = self.get_user_token(username='bap_koordinasyon_birimi_1')
            self.prepare_client('/bap_yurutucu_degisikligi_talebi', user=user, token=token)

            resp = self.client.post()

            assert resp.json['object']['Açıklama'] == 'Yeni yurutucu İsmet Tarhan olmasını istiyorum'
            assert resp.json['object']['Talep Edilen Yeni Yürütücü'] == str(yeni_okutman)
            assert resp.json['object']['Şuanki Yürütücü'] == str(okutman)

            if i == 0:
                self.client.post(form={'reddet': 1})

                resp = self.client.post(form={'red_aciklama': 'Red edildi.',
                                              'red_gonder': 1})
            else:
                resp = self.client.post(cmd='onayla', form={'onayla': 1})
                assert resp.json['forms']['schema']['title'] == 'Yürütücü Değişikliği Talebini' \
                                                                ' Komisyona Yolla'
                resp = self.client.post(form={'komisyona_gonder': 1})

            self.lane_change_massage_kontrol(resp)
