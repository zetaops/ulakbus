# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import BAPSSS

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_sss(self):
        yayinlanmis_sss_sayisi = BAPSSS.objects.all(yayinlanmis_mi=True).count()

        for i in range(2):
            self.prepare_client('/bap_sikca_sorulan_sorular', username='bap_koordinasyon_birimi_1')
            resp = self.client.post()
            soru_sayisi = len(resp.json['objects']) - 1
            if i == 1:
                time.sleep(1)
                yeni_yay_sss_sayisi = BAPSSS.objects.all(yayinlanmis_mi=True).count()
                assert yeni_yay_sss_sayisi == yayinlanmis_sss_sayisi + 1
                obj = BAPSSS.objects.all(soru='Test Sıkca Sorulan Soru?',
                                         cevap='Onun cevabı',
                                         yayinlanmis_mi=True)[0]
                resp = self.client.post(cmd='confirm_deletion', object_id=obj.key)
                assert resp.json['forms']['schema']['title'] == 'Silme İşlemi'
                assert resp.json['forms']['form'][0]['helpvalue'] == 'Test Sıkca Sorulan Soru? ' \
                                                                     'sorusunu silmek istiyor' \
                                                                     ' musunuz?'
                resp = self.client.post(cmd='delete', form={'evet': 1})
                assert soru_sayisi - 1 == len(resp.json['objects']) - 1
            else:
                resp = self.client.post(cmd='add_edit_form', form={'ekle': 1})

                assert 'soru' in resp.json['forms']['model']
                assert 'cevap' in resp.json['forms']['model']

                resp = self.client.post(cmd='save', form={'soru': 'Test Sıkca Sorulan Soru?',
                                                          'cevap': 'Onun cevabı',
                                                          'kaydet': 1})

                assert len(resp.json['objects']) - 1 == soru_sayisi + 1

                obj = BAPSSS.objects.all(soru='Test Sıkca Sorulan Soru?', cevap='Onun cevabı')[0]

                resp = self.client.post(cmd='show', object_id=obj.key)

                assert resp.json['object'][u'Sıkça Sorulan Soru'] == 'Test Sıkca Sorulan Soru?'
                assert resp.json['object'][u'Cevap'] == 'Onun cevabı'
                assert resp.json['object'][u'Yayınlanmış mı?'] == 'False'

                self.client.post(object_key=obj.key, form={'tamam': 1})

                assert not obj.yayinlanmis_mi

                self.client.post(cmd='yayinla', object_id=obj.key)

                obj.reload()

                assert obj.yayinlanmis_mi
