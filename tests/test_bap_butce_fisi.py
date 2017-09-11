# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPButcePlani
from ulakbus.models import BAPProje, User
from zengine.lib.test_utils import BaseTestCase
from zengine.models import WFInstance, Message
import time


class TestCase(BaseTestCase):
    """
    Koordinasyon birimi muhasebe kodları girişi testi.
    """
    def test_bap_butce_fisi(self):
        # Kullanıcıya login yaptırılır
        self.prepare_client('/bap_butce_fisi', username='bap_koordinasyon_birimi_1')
        # Proje id input olarak is akisina gönderilir.
        resp = self.client.post(bap_proje_id='WlRiJzMM4XExfmbgVyJDBZAUGg')
        # Gelen liste ile projenin sahip olduğu butce kalemlerinin sayisi kontrol edilir.
        assert len(resp.json['forms']['model']['ButceKalemList']) == BAPButcePlani.objects.all(
            ilgili_proje_id='WlRiJzMM4XExfmbgVyJDBZAUGg').count()

        form = {
            "kaydet": 1,
            "ButceKalemList": [
                {
                    "muhasebe_kod": "03.2.1.01",
                    "kod_adi": "Büro Malzemesi Alımları",
                    "ad": "Masa Lambası",
                    "key": "RTcF939bRmDaET4b5lLi9lrbPEh",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.02",
                    "kod_adi": "Büro Malzemesi Alımları",
                    "ad": "Sandalye",
                    "key": "6nc6cOtND2nzqAJ8WMhGJz6ATAa",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.01",
                    "kod_adi": "Büro Malzemesi Alımları",
                    "ad": "Çalışma Masası",
                    "key": "T315MMLAMm8BUy0yz2xnGGoxzGd",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.01",
                    "kod_adi": "Kırtasiye Alımları",
                    "ad": "USB Bellek",
                    "key": "WD0K3k6syBXJOX9hkS5wBmnCQBD",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.02",
                    "kod_adi": "Kırtasiye Alımları",
                    "ad": "Şeffaf Dosya",
                    "key": "Jj8IRgcmS6HFNKPegm5wASOjUAB",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.7.3.02",
                    "kod_adi": "VID200",
                    "ad": "Vida",
                    "key": "94FrwJMNAW9CmJQkqcTo8VUYusA",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.01",
                    "kod_adi": "Kırtasiye Alımları",
                    "ad": "Kağıt",
                    "key": "7uvtCCHGqcjnAdhVMDtBKYiFQ2T",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.2.1.01",
                    "kod_adi": "Kırtasiye Alımları",
                    "ad": "Silgi",
                    "key": "BNfJoUkHVZKH2dmjzZEuJST4its",
                    "muhasebe_kod_genel": 1
                },
                {
                    "muhasebe_kod": "03.7.2.01",
                    "kod_adi": "EE250",
                    "ad": "Arduino",
                    "key": "MpRqF2BZk6sMbi4QNkQvTNH1mVW",
                    "muhasebe_kod_genel": 1
                }
            ]
        }

        resp = self.client.post(form=form)

        assert resp.json['forms']['model']['ButceKalemList'][0]['muhasebe_kod'] == \
               form['ButceKalemList'][0]['muhasebe_kod']

        assert resp.json['forms']['model']['ButceKalemList'][0][
                   'muhasebe_kod'] == BAPButcePlani.objects.get(
            resp.json['forms']['model']['ButceKalemList'][0]['key']).muhasebe_kod

        self.client.post(cmd='geri')

        form['ButceKalemList'][0]['muhasebe_kod'] = "03.2.1.02"

        resp = self.client.post(form=form)

        assert resp.json['forms']['model']['ButceKalemList'][0]['muhasebe_kod'] == \
               form['ButceKalemList'][0]['muhasebe_kod']

        assert resp.json['forms']['model']['ButceKalemList'][0][
                   'muhasebe_kod'] == BAPButcePlani.objects.get(
            resp.json['forms']['model']['ButceKalemList'][0]['key']).muhasebe_kod

        self.client.post(cmd='bitir')
