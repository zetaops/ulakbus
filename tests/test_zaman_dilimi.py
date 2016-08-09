# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, ZamanDilimleri
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_zaman_dilimi(self):
        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        self.prepare_client('/zaman_dilimi_duzenle', user=usr)
        resp = self.client.post()
        for i in range(2):
            if i == 1:
                assert resp.json['objects'][1]['fields']['Zaman Aralığı'] == "09:00-12:00"
            else:
                assert resp.json['objects'][0][0] == 'Gün Dilimi'

            resp = self.client.post(cmd='degistir', zaman_dilimi='XUM8nQZv1eJ6cgyDXnvpVG9BmcA')

            assert resp.json['forms']['model']['baslangic_saat'] == '09'

            if i == 1:
                zaman_dilimi_form = {
                    'baslangic_saat': '10',
                    'baslangic_dakika': '00',
                    'bitis_saat': '12',
                    'bitis_dakika': '00',
                    'gun_dilimi': 'Sabah',
                    'kaydet': 1
                }
                resp = self.client.post(cmd='kayit', form=zaman_dilimi_form)

                assert resp.json['msgbox']['msg'] == "Kaydınız başarıyla gerçekleşti"
            else:
                resp = self.client.post(cmd='vazgec')

        resp = self.client.post(cmd='tamamla', form={'tamamla': 1})

        assert resp.json['msgbox']['title'] == 'Kayıt İşleminiz Tamamlanmıştır!'

        zd = ZamanDilimleri.objects.get('XUM8nQZv1eJ6cgyDXnvpVG9BmcA')

        assert zd.baslama_saat == '10'

        zd.baslama_saat = '09'
        zd.save()

        assert zd.baslama_saat == '09'
