# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPButcePlani, BAPProje, User, Personel

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_butce_plani(self):
        proje = BAPProje()
        user = User.objects.get(username='ogretim_uyesi_1')
        personel = Personel.objects.get(user=user)
        proje.ad = "Test ek bütçe talep projesi"
        proje.yurutucu = personel.okutman
        proje.save()

        muhasebe_kod = "03.2.1.01"
        butce_form = {'ad': "Test Defter",
                      'birim_fiyat': 12,
                      'adet': 1,
                      'gerekce': "Test Not tutulacak.",
                      'toplam_fiyat': 12.5,
                      'kaydet': 1}

        self.prepare_client('/bap_butce_plani', username="ogretim_uyesi_1")
        self.client.post()

        resp = self.client.post(form={'proje': proje.key, 'ilerle': 1})

        butce_planlari_sayisi = len(resp.json['objects'])

        resp = self.client.post(form={'add': 1}, cmd='add_edit_form')

        assert 'muhasebe_kod' in resp.json['forms']['model']

        self.client.post(form={'ilerle': 1, 'muhasebe_kod': muhasebe_kod})

        resp = self.client.post(form=butce_form)

        assert len(resp.json['objects']) == butce_planlari_sayisi + 1

        object_id = BAPButcePlani.objects.get(ad=butce_form['ad'],
                                              gerekce=butce_form['gerekce']).key

        resp = self.client.post(object_id=object_id, cmd='add_edit_form')

        assert resp.json['forms']['model']['muhasebe_kod'] == muhasebe_kod

        resp = self.client.post(form={'ilerle': 1,
                                      'model_type': "BAPButcePlani",
                                      'muhasebe_kod': muhasebe_kod,
                                      'object_key': object_id,
                                      'unicode': "03.2.1.01 / Kırtasiye Alımları / Test Defter"})

        assert resp.json['forms']['model']['ad'] == butce_form['ad']

        butce_form['adet'] = 2
        butce_form['toplam_fiyat'] = 25.0
        butce_form['gerekce'] = "Test düzenleme Not tutulacak."
        butce_form['object_key'] = object_id

        resp = self.client.post(form=butce_form)

        assert len(resp.json['objects']) == butce_planlari_sayisi + 1

        resp = self.client.post(object_id=object_id, cmd='show')

        assert resp.json['object'][u'Gerekçe'] == str(butce_form['gerekce'])
        assert resp.json['object'][u'Adet'] == str(butce_form['adet'])
        assert resp.json['object'][u'Toplam Fiyat'] == str(butce_form['toplam_fiyat'])

        self.client.post(object_key=object_id, form={'tamam': 1})

        resp = self.client.post(object_id=object_id, cmd='confirm_deletion')

        assert resp.json['forms']['form'][0]['helpvalue'] == "03.2.1.01 / Kırtasiye Alımları / " \
                                                             "Test Defter bilgilerine sahip " \
                                                             "bütçe planını silmek istiyormusunuz?"

        resp = self.client.post(form={'sil': 1}, cmd='delete')

        assert len(resp.json['objects']) == butce_planlari_sayisi
