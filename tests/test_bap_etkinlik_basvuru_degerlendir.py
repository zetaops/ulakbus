# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPGundem
from ulakbus.models import User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_etkinlik_basvuru_degerlendir(self):
        etkinlik_id = 'Yt4VkZQfnt9XEiSnMcZvUKUWSj'
        user = User.objects.get(username='bap_komisyon_uyesi_1')

        self.prepare_client('/bap_komisyon_uyesi_etkinlik_basvuru_degerlendir', user=user)
        self.client.post()

        resp = self.client.post(cmd='goruntule', object_id=etkinlik_id)

        assert resp.json['object_title'] == 'Bilimsel Etkinliklere Katılım Desteği : Çay Yaprağı ' \
                                            'Paradoksunda Akışkanlar Mekaniğinin Yeri | Henife ' \
                                            'Şener'

        resp = self.client.post(cmd='hakem')

        assert resp.json['forms']['schema']['title'] == 'Hakem Seç'

        resp = self.client.post(cmd='tamam', form={'hakem_id': '3X9GJ4Cm3gp2odCOaNj1eJtTT2h'})

        assert resp.json['forms']['form'][0][
                   'helpvalue'] == 'Seçtiğiniz hakeme basvuru değerlendirme daveti başarıyla ' \
                                   'gönderildi'

        self.client.post()

        user = User.objects.get(username='ogretim_elemani_2')

        gundem_sayisi = BAPGundem.objects.count()

        self.prepare_client('/bap_etkinlik_basvuru_degerlendir', user=user)
        self.client.current.task_data['etkinlik_basvuru_id'] = etkinlik_id
        self.client.current.task_data['hakem'] = True
        resp = self.client.post(object_id=etkinlik_id, hakem=True)

        assert resp.json['object_title'] == 'Bilimsel Etkinliklere Katılım Desteği : Çay Yaprağı ' \
                                            'Paradoksunda Akışkanlar Mekaniğinin Yeri | Henife ' \
                                            'Şener'

        resp = self.client.post(cmd='degerlendir')

        assert resp.json['forms']['schema']['title'] == 'Etkinlik Başvuru Değerlendir'

        form = {
            'aciklama': 'Olmamış',
            'sonuc': 2
        }

        resp = self.client.post(form=form, cmd='degerlendir')

        assert resp.json['forms']['form'][0][
                   'helpvalue'] == 'Çay Yaprağı Paradoksunda Akışkanlar Mekaniğinin Yeri ' \
                                   'Etkinlik Başvurusunu Başarıyla Değerlendirdiniz'

        assert BAPGundem.objects.count() == gundem_sayisi + 1
