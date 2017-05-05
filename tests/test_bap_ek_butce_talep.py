# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, Personel, User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def lane_change_massage_kontrol(self, resp):
        assert resp.json['msgbox']['title'] == 'Teşekkürler!'
        assert resp.json['msgbox']['msg'] == 'Bu iş akışında şuan için gerekli adımları ' \
                                             'tamamladınız. İlgili kişiler, iş akışına ' \
                                             'katılmaları için haberdar edildiler.'

    def test_bap_ek_butce_talep(self):
        proje = BAPProje()
        user = User.objects.get(username='ogretim_uyesi_1')
        personel = Personel.objects.get(user=user)
        proje.ad = "Test ek bütçe talep projesi"
        proje.yurutucu = personel
        proje.save()

        gundem_sayisi = BAPGundem.objects.filter(gundem_tipi=2, proje=proje).count()

        object_form = {'ad': 'Araba',
                             'adet': 1,
                             'birim_fiyat': 100,
                             'gerekce': 'Yol icin',
                             'toplam_fiyat': 120,
                             'kaydet': 1}
        butce = BAPButcePlani()

        for i in range(3):
            time.sleep(1)
            if i == 0:
                self.prepare_client('/bap_ek_butce_talep', user=user)
            else:
                token, user = self.get_user_token('ogretim_uyesi_1')
                self.prepare_client('/bap_ek_sure_talep', user=user, token=token)

            resp = self.client.post()

            if i == 2:
                assert resp.json['msgbox']['title'] == 'Talebiniz Kabul Edildi.'
                assert resp.json['msgbox']['msg'] == 'Ek bütçe için bulunduğunuz talep ' \
                                                     'kabul edilmiş olup, komisyonun ' \
                                                     'gündemine alınmıştır.'
                break

            kalem_sayisi = BAPButcePlani.objects.filter(ilgili_proje=proje).count()
            resp = self.client.post(form={'ilerle': 1, 'proje': proje.key})

            assert len(resp.json['objects']) - 2 == kalem_sayisi

            # ekleme
            if i == 0:
                self.client.post(form={'ekle': 1}, cmd='add_edit_form')
                resp = self.client.post(form={'muhasebe_kod': "03.5.5.02", 'ilerle': 1})
                assert resp.json['forms']['form'][0]['helpvalue'] == "Yapacaginiz butce plani " \
                                                                     "Test ek bütçe talep " \
                                                                     "projesi adli proje icin " \
                                                                     "yapilacaktir."
            elif i == 1:
                assert resp.json['msgbox']['title'] == 'Talebiniz Reddedildi.'
                assert resp.json['msgbox']['msg'] == 'Yeniden duzenleyiniz'

                self.client.post(cmd='add_edit_form', object_id=butce.key)
                resp = self.client.post(form={'muhasebe_kod': "03.5.5.02",
                                              'ilerle': 1,
                                              'model_type': 'BAPButcePlani',
                                              'object_key': butce.key})

                assert resp.json['forms']['model']['ad'] == object_form['ad']
                assert resp.json['forms']['model']['toplam_fiyat'] == object_form['toplam_fiyat']

                object_form['toplam_fiyat'] = 100
                object_form['gerekce'] = 'Indirim yapildi'

            resp = self.client.post(form=object_form)
            kalem_sayisi = BAPButcePlani.objects.filter(ilgili_proje=proje).count()
            if i == 0:
                butce = BAPButcePlani.objects.get(ilgili_proje=proje,
                                                  ad=object_form['ad'],
                                                  birim_fiyat=object_form['birim_fiyat'],
                                                  adet=object_form['adet'])

            assert len(resp.json['objects']) - 2 == kalem_sayisi

            # lane change
            resp = self.client.post(form={'tamam': 1})
            self.lane_change_massage_kontrol(resp)

            time.sleep(1)

            token, user = self.get_user_token(username='bap_koordinasyon_birimi_1')
            self.prepare_client('/bap_ek_sure_talep', user=user,
                                token=token)

            resp = self.client.post()
            assert resp.json['object_title'] == "Yürütücü: Henife Şener / Proje: Test ek " \
                                                "bütçe talep projesi - Ek bütçe talebi"
            assert resp.json['objects'][1]['fields'][1] == 'Araba'
            if i == 0:
                assert resp.json['objects'][1]['fields'][3] == '120'
                assert resp.json['objects'][1]['fields'][4] == 'Yol icin'
                assert resp.json['objects'][1]['fields'][5] == 'Yeni'
                self.client.post(cmd='iptal')

                resp = self.client.post(form={'red_aciklama': 'Yeniden duzenleyiniz',
                                              'red_gonder': 1})

            if i == 1:
                assert resp.json['objects'][1]['fields'][3] == '100'
                assert resp.json['objects'][1]['fields'][4] == 'Indirim yapildi'
                assert resp.json['objects'][1]['fields'][5] == 'Düzenlendi'

                resp = self.client.post(cmd='kabul', form={'onayla': 1})
                time.sleep(0.5)
                assert BAPGundem.objects.filter(gundem_tipi=2,
                                                proje=proje).count() == gundem_sayisi + 1

            self.lane_change_massage_kontrol(resp)

        proje.delete()
        butce.delete()
