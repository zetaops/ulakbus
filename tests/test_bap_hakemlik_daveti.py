# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User
from zengine.lib.test_utils import BaseTestCase
import time

from zengine.models import TaskInvitation


class TestCase(BaseTestCase):
    def test_bap_hakemlik_daveti(self):
        # Proje alınır.
        proje = BAPProje.objects.get('WlRiJzMM4XExfmbgVyJDBZAUGg')
        proje.reload()
        for degerlendirme in proje.ProjeDegerlendirmeleri:
            degerlendirme.remove()
        proje.blocking_save()
        proje.reload()
        # Koordinasyon birimi kullanıcısı alınır.
        user_koord = User.objects.get(username='bap_koordinasyon_birimi_1')
        # Koordinasyon birimi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_basvuru_listeleme', user=user_koord)
        self.client.post()
        # Hakem atama iş akışı başlatılır.
        self.client.post(cmd='hakem_daveti', object_id='WlRiJzMM4XExfmbgVyJDBZAUGg')
        # Başhan Yakuphanogullarından adlı ogretim elemanı kullanıcısı davet listesine eklenir.
        form = {
            'hakem': "3X9GJ4Cm3gp2odCOaNj1eJtTT2h",
            'ekle': 1
        }
        resp = self.client.post(cmd='ekle', form=form)

        assert resp.json['forms']['model']['Hakemler'][0]['soyad'] == 'Yakuphanoğullarından'
        assert resp.json['forms']['model']['Hakemler'][0]['durum'] == 1

        # Listeye davet gönderilir.
        resp = self.client.post(cmd='bitir')

        # Listeleme iş akışına dönülür.
        resp = self.client.post(cmd='tamam')

        time.sleep(1)

        # Hakem atama iş akışı tekrar başlatılır.
        resp = self.client.post(cmd='hakem_daveti', object_id='WlRiJzMM4XExfmbgVyJDBZAUGg')

        assert resp.json['forms']['model']['Hakemler'][0]['soyad'] == 'Yakuphanoğullarından'
        assert resp.json['forms']['model']['Hakemler'][0]['durum'] == 2

        form = {
            'hakem': "I1QVJUVQ2FydxNsxksJCXn9cdeT"
        }

        # Başka bir hakem adayı eklenir.
        self.client.post(cmd='ekle', form=form)

        form = {
            'hakem': "I1QVJUVQ2FydxNsxksJCXn9cdeT",
        }

        # Eklenen hakem adayı çıkarılır
        resp = self.client.post(cmd='cikar', form=form)
        # Davet listesinin boş olduğu kontrol edilir
        assert len(resp.json['forms']['model']['Hakemler']) == 1

    def test_bap_proje_degerlendirme(self):
        proje = BAPProje.objects.get('WlRiJzMM4XExfmbgVyJDBZAUGg')
        user = User.objects.get(username='ogretim_elemani_2')
        # Hakemlik davetinden gelen task invitation bulunur.
        task_inv = TaskInvitation.objects.filter(
            role=user.role_set[0].role, title='Bap Proje Degerlendirme')[0]
        token = task_inv.instance().key

        # Task invitationdaki workflow instance ile proje değerlendirme iş akışı başlatılır.
        self.prepare_client('/bap_proje_degerlendirme', user=user, token=token)
        resp = self.client.post()

        # Hakemlik daveti kabul edilir.
        resp = self.client.post(cmd='davet_kabul')

        assert resp.json['forms']['model']['form_name'] == 'GenelProjeForm'

        # Proje değerlendirme admına gidilir.
        resp = self.client.post(cmd='karar_ver')

        assert resp.json['forms']['model']['form_name'] == 'ProjeDegerlendirmeForm'

        form = {
            'arastirma_kapsam_tutar': 1,
            'arastirma_kapsam_tutar_gerekce': 'asd',
            'arastirmaci_bilgi_yeterlilik': 1,
            'arastirmaci_bilgi_yeterlilik_gerekce': 'asd',
            'basari_olcut_gercek': 1,
            'basari_olcut_gercek_gerekce': 'asd',
            'bilim_endustri_katki': 1,
            'bilim_endustri_katki_gerekce': 'asd',
            'butce_gorus_oneri': 'asd',
            'katki_beklenti': 1,
            'katki_beklenti_gerekce': 'asd',
            'literatur_ozeti': 1,
            'literatur_ozeti_gerekce': 'asd',
            'ozgun_deger': 1,
            'ozgun_deger_gerekce': 'asd',
            'proje_degerlendirme_sonucu': 1,
            'proje_gorus_oneri': 'asd',
            'yontem_amac_tutar': 1,
            'yontem_amac_tutar_gerekce': 'asd',
            'yontem_uygulanabilirlik': 1,
            'yontem_uygulanabilirlik_gerekce': 'asd'
        }

        self.client.post(cmd='kaydet', form=form)
        self.client.post(cmd='tamam')

        proje.reload()

        assert proje.ProjeDegerlendirmeleri[0].form_data

        for degerlendirme in proje.ProjeDegerlendirmeleri:
            degerlendirme.remove()
        proje.blocking_save()











