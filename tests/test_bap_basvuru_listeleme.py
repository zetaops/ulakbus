# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User
from zengine.lib.test_utils import BaseTestCase
from zengine.models import WFInstance, Message
import time


class TestCase(BaseTestCase):
    def test_bap_basvuru_listeleme(self):
        project = BAPProje.objects.get('WlRiJzMM4XExfmbgVyJDBZAUGg')
        user_ou = User.objects.get(username='ogretim_uyesi_1')
        user_koord = User.objects.get(username='bap_koordinasyon_birimi_1')
        wfi = WFInstance.objects.get(wf_object=project.key, finished=True)

        assert wfi._data['data']['GenelBilgiGirForm']['ad'] == 'Akıllı Robot'
        assert project.durum == 4
        assert 'End' in wfi.step

        self.prepare_client('/bap_basvuru_listeleme', user=user_koord)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        assert 'Durum' and 'Proje_Adı' and 'Personel' in resp.json['objects'][0]
        assert resp.json['objects'][1]['fields'][1] == "Akıllı Robot"

        resp = self.client.post(cmd='incele', object_id=project.key,
                                wf="bap_basvuru_listeleme")

        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'
        assert 'Proje Adı' and 'Hedef ve Amaç' and 'B Planı' in resp.json['object'].keys()
        assert resp.json['object'][u'Proje Adı'] == u'Akıllı Robot'

        resp = self.client.post(cmd='butce_plani', wf='bap_basvuru_listeleme',
                                form={'butce_plani': 1})
        assert resp.json['forms']['schema']['title'] == 'Bütçe Planı'
        assert 'Muhasebe Kodu' and 'Kod Adı' in resp.json['objects'][0]

        resp = self.client.post(cmd='proje_calisanlari', wf='bap_basvuru_listeleme',
                                form={'proje_calisanlari': 1})
        assert resp.json['forms']['schema']['title'] == 'Proje Çalışanları'

        resp = self.client.post(cmd='is_plani', wf='bap_basvuru_listeleme',
                                form={'is_plani': 1})
        assert resp.json['forms']['schema']['title'] == 'İş Planı'

        resp = self.client.post(cmd='ayrinti', wf='bap_basvuru_listeleme',
                                data_key='QFf918chMLclolXnMbbF56NAbxd')
        assert resp.json['forms']['schema']['title'] == 'Robot Yazılımı İş Planı Ayrıntıları'

        resp = self.client.post(cmd='is_plani', wf='bap_basvuru_listeleme',
                                form={'form_name': 'IsPlaniAyrintilariForm', 'tamam': 1})
        assert resp.json['forms']['schema']['title'] == 'İş Planı'

        resp = self.client.post(cmd='iptal', wf='bap_basvuru_listeleme',
                                form={'iptal': 1})
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'

        self.client.post(cmd='incele', object_id=project.key,
                         wf="bap_basvuru_listeleme")

        resp = self.client.post(cmd='karar_ver', wf='bap_basvuru_listeleme',
                                form={'karar_ver': 1})
        assert resp.json['forms']['schema']['title'] == "İnceleme Sonrası Proje Kararı"
        assert 'Henife Şener' and 'Akıllı Robot' in resp.json['forms']['form'][0]['helpvalue']

        resp = self.client.post(cmd='iptal', wf='bap_basvuru_listeleme',
                                form={'iptal': 1})
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        self.client.post(cmd='incele', object_id=project.key,
                         wf="bap_basvuru_listeleme")
        self.client.post(cmd='karar_ver', object_id=project.key,
                         form={'karar_ver': 1})
        resp = self.client.post(cmd='revizyon', wf='bap_basvuru_listeleme',
                                form={'revizyon': 1})
        assert resp.json['forms']['schema']['title'] == "Revizyon İsteme Gerekçeleri"
        resp = self.client.post(cmd='gonder', wf='bap_basvuru_listeleme',
                                form={'gonder': 1, 'revizyon_gerekce': 'test-revizyon-gerekçe'})
        assert resp.json['msgbox']['title'] == "Kararınız İletildi"
        assert 'Henife Şener' and 'Akıllı Robot' in resp.json['msgbox']['msg']
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        project.reload()
        wfi.reload()
        assert project.durum == 3
        assert wfi.finished == False
        assert 'bap' in wfi.step

        self.client.post(wf='logout')

        self.prepare_client('/bap_proje_basvuru', user=user_ou, token=wfi.key)
        resp = self.client.post()
        assert 'Akıllı Robot' in resp.json['forms']['schema']['title']
        assert 'Revizyon Gerekçeleri' and 'test-revizyon-gerekçe' in resp.json['forms']['form'][0][
            'helpvalue']
        resp = self.client.post(wf='bap_proje_basvuru', form={'devam': 1})
        assert resp.json['forms']['schema']['title'] == "Proje Türü Seçiniz"
        self.client.post(cmd='kaydet_ve_kontrol', wf='bap_proje_basvuru', form={'sec': 1})

        resp = self.client.post(cmd='genel', wf='bap_proje_basvuru', form={'belgelerim_hazir': 1})
        assert resp.json['forms']['schema']['title'] == "Proje Genel Bilgileri"
        assert resp.json['forms']['model']['ad'] == 'Akıllı Robot'
        resp = self.client.post(wf='bap_proje_basvuru', form={'ad': 'Otomatik Süpürge',
                                                              'teklif_edilen_baslama_tarihi': "29.04.2017",
                                                              'detay_gir': 1})
        assert resp.json['forms']['schema']['title'] == 'Proje Detayları'
        assert 'Lorem ipsum' in resp.json['forms']['model']['hedef_ve_amac']
        resp = self.client.post(wf='bap_proje_basvuru', form={'proje_belgeleri': 1})
        assert resp.json['forms']['schema']['title'] == 'Proje Belgeleri'
        resp = self.client.post(wf='bap_proje_basvuru', form={'arastirma_olanaklari': 1})
        assert resp.json['forms']['schema']['title'] == 'Araştırma Olanakları Ekle'
        assert 'Endüstriyel' in resp.json['forms']['model']['Olanak'][0]['ad']
        resp = self.client.post(cmd='ilerle', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Çalışan Ekle"
        assert resp.json['forms']['model']['Calisan'][0]['ad'] == 'Kerim'

        self.client.post(cmd='ileri', wf='bap_proje_basvuru', form={'ileri': 1})
        self.client.post(wf='bap_proje_basvuru', form={'button': 1})
        resp = self.client.post(wf='bap_proje_basvuru', form={'button': 1})

        assert resp.json['forms']['schema']['title'] == "Üniversite Dışı Uzman Ekle"
        resp = self.client.post(wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Üniversite Dışı Destek Ekle"
        resp = self.client.post(wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Yürütücü Tecrübesi"
        resp = self.client.post(cmd='ileri', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Yürütücünün Halihazırdaki Projeleri"
        resp = self.client.post(cmd="ileri", wf='bap_proje_basvuru',
                                form={'ileri': 1, 'form_name': "YurutucuProjeForm"})

        assert 'Otomatik Süpürge' in resp.json['object_title']
        assert resp.json['object'][u'Proje Adı'] == u'Otomatik Süpürge'
        resp = self.client.post(cmd='onay', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['msgbox']['title'] == "Teşekkürler!"

        project.reload()
        assert project.durum == 2
        self.client.post(wf='logout')

        self.prepare_client('/bap_basvuru_listeleme', user=user_koord, token=wfi.key)
        resp = self.client.post()
        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'
        assert resp.json['object'][u'Proje Adı'] == u'Otomatik Süpürge'
        resp = self.client.post(cmd='karar_ver', wf='bap_basvuru_listeleme',
                                form={'karar_ver': 1})
        assert resp.json['forms']['schema']['title'] == "İnceleme Sonrası Proje Kararı"
        resp = self.client.post(cmd='onayla', wf='bap_basvuru_listeleme',
                                form={'karar_ver': 1})
        assert 'Otomatik Süpürge' in resp.json['forms']['schema']['title']
        assert 'Otomatik Süpürge' in resp.json['forms']['form'][0]['helpvalue']
        self.client.post(cmd='onayla', wf='bap_basvuru_listeleme', form={'tamam': 1})

        time.sleep(1)
        notification = Message.objects.filter().order_by()[0]
        project.reload()
        wfi.reload()
        assert project.durum == 4
        assert wfi.finished == True
        assert 'End' in wfi.step
        assert 'Otomatik Süpürge' in notification.msg_title
        assert 'gündeme alınmıştır' in notification.body
        assert notification.sender.key == user_koord.key
        assert notification.receiver.key == user_ou.key
        assert wfi._data['data']['GenelBilgiGirForm']['ad'] == 'Otomatik Süpürge'

        wfi._data['data']['GenelBilgiGirForm']['ad'] = 'Akıllı Robot'
        wfi.save()
        project.ad = 'Akıllı Robot'
        project.save()

        BAPProje.objects.filter(durum=None).delete()
