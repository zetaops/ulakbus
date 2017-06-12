# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from datetime import datetime

from ulakbus.models import BAPDuyuru

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_duyurular(self):
        yayinlanmis_duyuru_sayisi = BAPDuyuru.objects.all(yayinlanmis_mi=True).count()

        eklenme_tarihi = datetime.strptime('06.06.2017', '%d.%m.%Y').date()
        son_gecerlilik_tarihi = datetime.strptime('30.06.2017', '%d.%m.%Y').date()

        for i in range(2):
            self.prepare_client('/bap_duyurular', username='bap_koordinasyon_birimi_1')
            resp = self.client.post()
            soru_sayisi = len(resp.json['objects']) - 1
            if i == 1:
                time.sleep(1)
                yeni_yay_duyuru_sayisi = BAPDuyuru.objects.all(yayinlanmis_mi=True).count()
                assert yeni_yay_duyuru_sayisi == yayinlanmis_duyuru_sayisi + 1
                obj = BAPDuyuru.objects.all(duyuru_baslik='Duyuru İçin Gerekli Başlık',
                                               eklenme_tarihi=eklenme_tarihi,
                                               son_gecerlilik_tarihi=son_gecerlilik_tarihi,
                                               yayinlanmis_mi=True)[0]
                resp = self.client.post(cmd='confirm_deletion', object_id=obj.key)
                assert resp.json['forms']['schema']['title'] == 'Silme İşlemi'
                assert resp.json['forms']['form'][0]['helpvalue'] == 'Duyuru İçin Gerekli Başlık ' \
                                                                     'duyurusunu silmek ' \
                                                                     'istiyor musunuz?'
                resp = self.client.post(cmd='delete', form={'evet': 1})
                assert soru_sayisi - 1 == len(resp.json['objects']) - 1
            else:
                resp = self.client.post(cmd='add_edit_form', form={'ekle': 1})

                assert 'duyuru_baslik' in resp.json['forms']['model']
                assert 'duyuru_icerik' in resp.json['forms']['model']

                resp = self.client.post(cmd='save',
                                        form={'eklenme_tarihi': '06.06.2017',
                                              'son_gecerlilik_tarihi': '30.06.2017',
                                              'duyuru_baslik': 'Duyuru İçin Gerekli Başlık',
                                              'duyuru_icerik': 'ljsndlasjdnaskjdnaskljdasnlkdjn'
                                                               'adksjasdjansldkjansldjka',
                                              'kaydet': 1,
                                              'EkDosyalar': [
                                                  {'dosya_aciklamasi': 'test belgesi içeriğinde '
                                                                       'bulunanlar gereklidir.',
                                                   'ek_dosya':
                                                       {'file_content': 'data:text/plain;'
                                                                        'base64,dGVzdA==',
                                                        'file_name': 'test.txt',
                                                        'isImage': False}}]})

                assert len(resp.json['objects']) - 1 == soru_sayisi + 1
                obj = BAPDuyuru.objects.all(duyuru_baslik='Duyuru İçin Gerekli Başlık',
                                               eklenme_tarihi=eklenme_tarihi,
                                               son_gecerlilik_tarihi=son_gecerlilik_tarihi)[0]

                resp = self.client.post(cmd='show', object_id=obj.key)

                assert resp.json['object']['Başlık'] == 'Duyuru İçin Gerekli Başlık'
                assert resp.json['object']['Duyuru'] == 'ljsndlasjdnaskjdnaskljdasnlkdjn' \
                                                         'adksjasdjansldkjansldjka'
                assert resp.json['object']['Durum'] == 'Yayınlanmadı'

                self.client.post(object_key=obj.key, form={'tamam': 1})
                self.client.post(cmd='yayinla', object_id=obj.key)

                obj.reload()

                assert obj.yayinlanmis_mi
