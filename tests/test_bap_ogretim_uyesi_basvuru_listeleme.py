# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_ogretim_uyesi_basvuru_listele(self):
        # Öğretim üyesi kullanıcısı alınır.
        user_ou = User.objects.get(username='ogretim_uyesi_1')

        okutman = user_ou.personel.okutman
        proje_sayisi = BAPProje.objects.filter(yurutucu=okutman).count()

        # Ogretim uyesi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_ogretim_uyesi_basvuru_listeleme', user=user_ou)
        resp = self.client.post()

        # Kullanıcının proje sayısı kontrol edilir
        assert proje_sayisi + 1 == len(resp.json['objects'])

        # Durumu onaylanmış olan projelerde görüntüle dışındaki action butonlarının olduğu kontrol
        # edilir.
        for i in range(1, len(resp.json['objects'])):
            obj = resp.json['objects'][i]
            if BAPProje.objects.get(obj['key']).durum == 5:
                assert len(obj['actions']) > 1
            else:
                assert len(obj['actions']) == 1

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Ek bütçe talebine gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 1})

        # Ek bütçe adımına gelindiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_ek_butce_talep'

        # Ek bütçe adımı iptal edilerek listeleme adımına dönülür.
        self.client.post(cmd='iptal')

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Ek süre adımına gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 3})

        # Ek süre adımına gidildiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_ek_sure_talep'

        # Ek süre adımı kontrol edilir.
        self.client.post(cmd='iptal')

        # Talep seçme adımına gidilir.
        self.client.post(cmd='talepler', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Fasıl aktarımı adımına gidilir.
        resp = self.client.post(form={'sec': 1, 'talepler': 2})

        # Fasıl aktarımı adımına gidildiği kontrol edilir.
        assert resp.json['wf_meta']['name'] == 'bap_fasil_aktarim_talep'
