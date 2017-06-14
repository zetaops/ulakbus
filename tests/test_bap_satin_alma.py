# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPButcePlani
from ulakbus.models import BAPProje, User
from ulakbus.models import BAPSatinAlma
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.translation import gettext as _

from zengine.models import TaskInvitation


class TestCase(BaseTestCase):
    def test_bap_satin_alma(self):
        # Proje alınır.
        proje = BAPProje.objects.get('b5avq6Tc6jHuKf9z2kizPFK3nc')

        # Koordinasyon birimi kullanıcısı alınır.
        user_koord = User.objects.get(username='bap_koordinasyon_birimi_1')

        # Koordinasyon birimi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_basvuru_listeleme', user=user_koord)
        self.client.post()

        # Satın alma iş akışı başlatılır.
        resp = self.client.post(cmd='satin_alma', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        butce_kalem_sayisi = BAPButcePlani.objects.filter(
            ilgili_proje=proje, satin_alma_durum=1).count()

        assert len(resp.json['forms']['model']['Kalem']) == butce_kalem_sayisi

        form = {
            "Kalem": [
                {
                    "ad": "Mazot",
                    "adet": 10,
                    "alim_kalemi_sartnamesi": "",
                    "butce_plan_key": "8W16zg1iEvrrbQXRpM4JFw3oR62",
                    "genel_sartname": "",
                    "sec": False
                },
                {
                    "ad": "Koltuk Takımı Alımı",
                    "adet": 2,
                    "alim_kalemi_sartnamesi": "",
                    "butce_plan_key": "9Q23XOLMGDUlvTZAfTew8nzetWr",
                    "genel_sartname": "",
                    "sec": False
                }
            ],
            "tamam": 1
        }

        resp = self.client.post(form=form, cmd='tamam')

        assert "msgbox" in resp.json

        form['Kalem'][0]['sec'] = True

        self.client.post(form=form, cmd='tamam')

        form = {
            "aciklama": "asd",
            "ekleyen": "UJmuvhQ32fWfxXYuUkoS9gFHfrw",
            "kaydet": 1,
            "onay_tarih_sayi": "123",
            "satin_alma_talep_adi": "Başlık",
            "son_teklif_tarihi": "14.06.2017",
            "teklife_acilma_tarihi": "14.06.2017",
            "yurutucu": "G2XjlaJMX0FUZX84aoIeiVCqZMR"
        }

        resp = self.client.post(form=form, cmd='kaydet')

        assert resp.json['forms']['form'][0]['helpvalue'] == _(
            u"Satın alma talebi başarıyla oluşturuldu.")

        self.client.post(form={"tamam": 1})

        resp = self.client.post(cmd='satin_alma', object_id='b5avq6Tc6jHuKf9z2kizPFK3nc')

        assert len(resp.json['forms']['model']['Kalem']) == butce_kalem_sayisi - 1

        BAPSatinAlma.objects.get(ekleyen_id="UJmuvhQ32fWfxXYuUkoS9gFHfrw",
                                 aciklama="asd", ad="Başlık").blocking_delete()

        butce = BAPButcePlani.objects.get('8W16zg1iEvrrbQXRpM4JFw3oR62')
        butce.satin_alma_durum = 1
        butce.blocking_save()
