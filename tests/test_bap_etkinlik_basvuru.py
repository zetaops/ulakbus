# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import User

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_bap_etkinlik_basvuru(self):
        # Ogretim uyesi kullanicisi alinir
        user = User.objects.get(username='ogretim_uyesi_1')
        # Etkinlik basvuru is akisi baslatilir
        self.prepare_client('/bap_etkinlik_basvuru', user=user)
        self.client.post()

        onceki_etkinlik_sayisi = BAPEtkinlikProje.objects.count()

        form = {
            'baslangic': '01.08.2017',
            'bildiri_basligi': 'Neron Öncesi ve Neron Sonrası Roma Mimarisi',
            'bitis': '01.08.2017',
            'etkinlik_lokasyon': 1,
            'ileri': 1,
            'katilim_turu': 2,
            'sehir': 'Roma',
            'ulke': 'İtalya'
        }

        resp = self.client.post(form=form)

        assert resp.json['forms']['model']['form_name'] == 'ButcePlanForm'

        form = {
            'Butce': [
                {
                    'istenen_tutar': 1000,
                    'talep_turu': 1
                },
                {
                    'istenen_tutar': 1000,
                    'talep_turu': 2
                },
                {
                    'istenen_tutar': 1000,
                    'talep_turu': 3
                },
                {
                    'istenen_tutar': 1000,
                    'talep_turu': 4
                }
            ]
        }

        resp = self.client.post(form=form)

        assert resp.json['forms']['form'][0]['helpvalue'] == 'Pasaport Giriş Çıkış Fotokopi'

        resp = self.client.post(form={'ileri': 1})

        assert resp.json['forms']['form'][0][
                   'helpvalue'] == 'Başvurunuz BAP birimine başarıyla iletilmiştir. ' \
                                    'Değerlendirme sürecinde size bilgi verilecektir.'

        assert BAPEtkinlikProje.objects.count() == onceki_etkinlik_sayisi + 1

        BAPEtkinlikProje.objects.get(
            bildiri_basligi='Neron Öncesi ve Neron Sonrası Roma Mimarisi').blocking_delete()

        assert BAPEtkinlikProje.objects.count() == onceki_etkinlik_sayisi
