# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, ZamanCetveli, DerslikZamanPlani
from zengine.lib.test_utils import BaseTestCase
import time
from zengine.messaging.model import Message


class TestCase(BaseTestCase):

    def test_zaman_tablo(self):
        for loop in range(2):
            time.sleep(1)
            if loop == 1:
                token, user = self.get_user_token('ders_programi_koordinatoru_1')
                self.prepare_client('/ogretim_elemani_zaman_tablosu', user=user, token=token)
                resp = self.client.post()
                assert resp.json['msgbox']['msg'] == "Reddedildi"
                Message.objects.filter().delete()
            else:
                usr = User.objects.get(username='ders_programi_koordinatoru_1')
                self.prepare_client('/ogretim_elemani_zaman_tablosu', user=usr)
                resp = self.client.post()
                assert len(resp.json['ogretim_elemani_zt']['uygunluk_durumu']) == 21

            oe_change_key = '5T0d4wccvvkwRgRAIyZQoK3iQnP'
            oe_change_durum = 1

            item_durum = {'key': oe_change_key,
                          'durum': oe_change_durum}

            resp = self.client.post(cmd='degistir', change=item_durum)
            zc = ZamanCetveli.objects.get(oe_change_key)
            assert zc.durum == 1 and resp.json['kayit_durum']

            zc.durum = 3
            zc.save()

            item_key = {'key': 'GIga2Cy4iYV4rwfCs9SjVqyygFg'}
            resp = self.client.post(cmd='personel_sec', secili_og_elemani=item_key)
            assert resp.json['ogretim_elemani_zt']['oe_key'] == 'GIga2Cy4iYV4rwfCs9SjVqyygFg'

            for i in range(2):
                resp = self.client.post(cmd='gonder')
                assert resp.json['forms']['schema']['title'] == 'Öğretim Elemanı Ders Programını ' \
                                                                'Bölüm Başkanına yollamak istiyor musunuz?'
                if i == 0:
                    resp = self.client.post(cmd='hayir')
                    assert resp.json['ogretim_elemani_zt']['oe_key'] == 'GIga2Cy4iYV4rwfCs9SjVqyygFg'
                else:
                    resp = self.client.post(cmd='evet')
                    assert resp.json['msgbox']['title'] == 'Onay İçin Gonderildi!'

            time.sleep(1)

            token, user = self.get_user_token('bolum_baskani_2')
            self.prepare_client('/ogretim_elemani_zaman_tablosu', user=user, token=token)
            resp = self.client.post()
            Message.objects.filter().delete()
            assert len(resp.json['ogretim_elemani_zt']['uygunluk_durumu']) == 21

            resp = self.client.post(cmd='kontrol', secili_og_elemani=item_key)
            assert resp.json['ogretim_elemani_zt']['oe_key'] == 'GIga2Cy4iYV4rwfCs9SjVqyygFg'
            if loop == 1:
                resp = self.client.post(cmd='onay')
                assert resp.json['msgbox']['title'] == 'Öğretim Elemani Zaman Tablosunu Onayladınız!'
            else:
                self.client.post(cmd='reddet')
                resp = self.client.post(form={"gonder": 1,
                                              "mesaj": "Reddedildi"})
                assert resp.json['msgbox']['title'] == "Red Açıklaması Gönderildi!"
        time.sleep(1)

        token, user = self.get_user_token('ders_programi_koordinatoru_1')
        self.prepare_client('/ogretim_elemani_zaman_tablosu', user=user, token=token)
        resp = self.client.post()
        assert resp.json['msgbox']['title'] == 'Talebiniz Onaylandı!'
        Message.objects.filter().delete()

    def test_derslik_zaman_tablosu(self):
        for loop in range(2):
            time.sleep(1)
            if loop == 1:
                token, user = self.get_user_token('ders_programi_koordinatoru_1')
                self.prepare_client('/derslik_zaman_tablosu', user=user, token=token)
                resp = self.client.post()
                assert resp.json['msgbox']['msg'] == "Reddedildi"
                Message.objects.filter().delete()
            else:
                usr = User.objects.get(username='ders_programi_koordinatoru_1')
                self.prepare_client('/derslik_zaman_tablosu', user=usr)
                resp = self.client.post()
                assert len(resp.json['derslik_zaman_tablosu']) == 5

            derslik_key = "SaVEo6G1fiR8vQQZXUZtzPqpUsl"
            derslik_durum = 3

            item_durum = {'key': derslik_key,
                          'durum': derslik_durum}

            resp = self.client.post(cmd='degistir', change=item_durum)
            dz = DerslikZamanPlani.objects.get(derslik_key)
            assert dz.derslik_durum == 3 and resp.json['kayit_durum']

            dz.derslik_durum = 1
            dz.save()

            item_key = {'key': "7X1vt5NTFNOaxG0qpR7K80eBqRp"}
            resp = self.client.post(cmd='derslik_degistir', secili_derslik=item_key)
            assert resp.json['derslik_zaman_tablosu']['derslik_key'] == "7X1vt5NTFNOaxG0qpR7K80eBqRp"

            for i in range(2):
                resp = self.client.post(cmd='gonder')
                assert resp.json['forms']['schema']['title'] == 'Derslik Ders Programını ' \
                                                                'Bölüm Başkanına yollamak istiyor musunuz?'
                if i == 0:
                    resp = self.client.post(cmd='hayir')
                    assert resp.json['derslik_zaman_tablosu']['derslik_key'] == "7X1vt5NTFNOaxG0qpR7K80eBqRp"
                else:
                    resp = self.client.post(cmd='evet')
                    assert resp.json['msgbox']['title'] == 'Onay İçin Gönderildi!'

            time.sleep(1)

            token, user = self.get_user_token('bolum_baskani_2')
            self.prepare_client('/derslik_zaman_tablosu', user=user, token=token)
            resp = self.client.post()
            Message.objects.filter().delete()
            assert len(resp.json['derslik_zaman_tablosu']) == 6

            resp = self.client.post(cmd='kontrol', secili_derslik=item_key)
            assert resp.json['derslik_zaman_tablosu']['derslik_key'] == "7X1vt5NTFNOaxG0qpR7K80eBqRp"
            if loop == 1:
                resp = self.client.post(cmd='onay')
                assert resp.json['msgbox']['title'] == 'Derslik Zaman Tablosunu Onayladınız!'
            else:
                self.client.post(cmd='reddet')
                resp = self.client.post(form={"gonder": 1,
                                              "mesaj": "Reddedildi"})
                assert resp.json['msgbox']['title'] == "Red Açıklaması Gönderildi!"

        time.sleep(1)

        token, user = self.get_user_token('ders_programi_koordinatoru_1')
        self.prepare_client('/derslik_zaman_tablosu', user=user, token=token)
        resp = self.client.post()
        assert resp.json['msgbox']['title'] == 'Talebiniz Onaylandı!'
        Message.objects.filter().delete()
