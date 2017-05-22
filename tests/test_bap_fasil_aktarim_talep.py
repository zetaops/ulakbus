# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def lane_change_massage_kontrol(self, resp):
        assert resp.json['msgbox']['title'] == 'Teşekkürler!'
        assert resp.json['msgbox']['msg'] == 'Bu iş akışında şuan için gerekli adımları ' \
                                             'tamamladınız. İlgili kişiler, iş akışına ' \
                                             'katılmaları için haberdar edildiler.'

    def test_bap_fasil_aktarim_talep(self):
        proje = BAPProje()
        user = User.objects.get(username='ogretim_uyesi_1')
        proje.ad = "Test ek bütçe talep projesi"
        proje.yurutucu = user.personel
        proje.kabul_edilen_butce = 100.0
        proje.save()

        obj_data = {'butce1': {'ad': 'Benzin',
                               'adet': 10,
                               'birim_fiyat': 5.10,
                               'toplam_fiyat': 51.10,
                               'gerekce': 'Araba yakıtı için',
                               'muhasebe_kod': '03.2.3.02'},
                    'butce2': {'ad': 'Araba',
                               'adet': 1,
                               'birim_fiyat': 40.40,
                               'toplam_fiyat': 40.40,
                               'gerekce': 'Yol için',
                               'muhasebe_kod': '03.5.5.02'}}

        butce1 = BAPButcePlani()
        butce1.ad = obj_data['butce1']['ad']
        butce1.adet = obj_data['butce1']['adet']
        butce1.birim_fiyat = obj_data['butce1']['birim_fiyat']
        butce1.gerekce = obj_data['butce1']['gerekce']
        butce1.muhasebe_kod = obj_data['butce1']['muhasebe_kod']
        butce1.toplam_fiyat = obj_data['butce1']['toplam_fiyat']
        butce1.ilgili_proje = proje
        butce1.save()
        obj_data['butce1']['ilerle'] = 1
        obj_data['butce1']['object_key'] = butce1.key

        butce2 = BAPButcePlani()
        butce2.ad = obj_data['butce2']['ad']
        butce2.adet = obj_data['butce2']['adet']
        butce2.birim_fiyat = obj_data['butce2']['birim_fiyat']
        butce2.gerekce = obj_data['butce2']['gerekce']
        butce2.muhasebe_kod = obj_data['butce2']['muhasebe_kod']
        butce2.toplam_fiyat = obj_data['butce2']['toplam_fiyat']
        butce2.ilgili_proje = proje
        butce2.save()
        obj_data['butce2']['ilerle'] = 1
        obj_data['butce2']['object_key'] = butce2.key

        # --------------Proje Yürütücüsü---------------
        self.prepare_client('/bap_fasil_aktarim_talep', user=user)

        self.client.post()

        self.client.post(form={'proje': proje.key, 'ilerle': 1})

        # butce1 duzenleme
        resp = self.client.post(cmd='add_edit_form', object_id=butce1.key)

        for k, v in obj_data['butce1'].iteritems():
            if k not in ['muhasebe_kod', 'ad', 'ilerle']:
                assert resp.json['forms']['model'][k] == v

        obj_data['butce1']['toplam_fiyat'] = 1000

        # butce1 fazla tutar girme
        resp = self.client.post(form=obj_data['butce1'])

        assert resp.json['msgbox']['title'] == 'Bütçe Fazlası!'
        assert resp.json['msgbox']['msg'] == 'Kabul edilen toplam bütçeden fazlasını ' \
                                             'talep edemezsiniz.'
        obj_data['butce1']['toplam_fiyat'] = 51.10

        # butce1 yeniden duzenleme
        resp = self.client.post(cmd='add_edit_form', object_id=butce1.key)

        for k, v in obj_data['butce1'].iteritems():
            if k not in ['muhasebe_kod', 'ad', 'ilerle']:
                assert resp.json['forms']['model'][k] == v

        obj_data['butce1']['adet'] = 5
        obj_data['butce1']['toplam_fiyat'] = 25.50

        resp = self.client.post(form=obj_data['butce1'])
        assert 'aciklama' in resp.json['forms']['model']

        # butce1 aciklama yazma
        self.client.post(form={'aciklama': 'Yakıt için gerekli benzin litresi düşürüldü',
                               'kaydet': 1})

        # butce1 goruntuleme
        resp = self.client.post(cmd='show', object_id=butce1.key)

        assert resp.json['object']['Yeni Adet'] == str(obj_data['butce1']['adet'])
        assert resp.json['object']['Yeni Toplam Fiyat'] == str(obj_data['butce1']['toplam_fiyat'])

        self.client.post(form={'tamam': 1})

        # butce2 duzenleme
        resp = self.client.post(cmd='add_edit_form', object_id=butce2.key)

        for k, v in obj_data['butce2'].iteritems():
            if k not in ['muhasebe_kod', 'ad', 'ilerle']:
                assert resp.json['forms']['model'][k] == v

        obj_data['butce1']['birim_fiyat'] = 70.30
        obj_data['butce1']['toplam_fiyat'] = 70.30

        resp = self.client.post(form=obj_data['butce2'])
        assert 'aciklama' in resp.json['forms']['model']

        # butce2 aciklama yazma
        self.client.post(form={'aciklama': 'Kiralanacak aracın fiyatı arttı.',
                               'kaydet': 1})

        # butce2 goruntuleme
        resp = self.client.post(cmd='show', object_id=butce2.key)
        assert resp.json['object'][u'Yeni Birim Fiyat'] == str(obj_data['butce2']['birim_fiyat'])
        assert resp.json['object'][u'Yeni Toplam Fiyat'] == str(obj_data['butce2']['toplam_fiyat'])

        self.client.post(form={'tamam': 1})

        # bap koordinasyon birimine yollandi
        resp = self.client.post(cmd='yolla', form={'tamam': 1})
        self.lane_change_massage_kontrol(resp=resp)

        # ----------------------------------------------

        time.sleep(1)

        # ------------Bap Koordinasyon Birimi-----------
        token, user = self.get_user_token(username='bap_koordinasyon_birimi_1')
        self.prepare_client('/bap_fasil_aktarim_talep', user=user,
                            token=token)
        resp = self.client.post()

        assert len(resp.json['objects']) - 1 == 2

        resp = self.client.post(cmd='show', object_id=butce1.key)

        assert resp.json['object']['Açıklama'] == 'Yakıt için gerekli benzin litresi düşürüldü'
        assert resp.json['object']['Eski Adet'] == '10'
        assert resp.json['object']['Yeni Adet'] == '5'
        assert resp.json['object']['Eski Toplam Fiyat'] == '51.1'
        assert resp.json['object']['Yeni Toplam Fiyat'] == '25.5'

        self.client.post(form={'tamam': 1})

        resp = self.client.post(cmd='kabul', form={'onayla': 1})

        assert 'komisyon_aciklama' in resp.json['forms']['model']

        resp = self.client.post(form={'komisyon_aciklama': 'Kontrol Edildi.',
                                      'yolla': 1})

        self.lane_change_massage_kontrol(resp)

        time.sleep(1)

        token, user = self.get_user_token('ogretim_uyesi_1')
        self.prepare_client('/bap_ek_sure_talep', user=user, token=token)

        resp = self.client.post()
        assert resp.json['msgbox']['title'] == 'Talebiniz Komisyon Gündemine Alınmıştır'
        assert resp.json['msgbox']['msg'] == 'Fasıl aktarımı için bulunduğunuz talep ' \
                                             'kabul edilmiş olup, komisyonun ' \
                                             'gündemine alınmıştır.'

        gundem = BAPGundem.objects.get(proje=proje)

        assert gundem.gundem_aciklama == 'Kontrol Edildi.'
        assert gundem.gundem_tipi == 3

        proje.delete()
        butce1.delete()
        butce2.delete()
        gundem.delete()


