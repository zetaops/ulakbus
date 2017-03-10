# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Atama, HizmetKayitlari, Personel
from ulakbus.models.auth import User
from zengine.lib.test_utils import BaseTestCase
from ulakbus.settings import DATE_DEFAULT_FORMAT, DATETIME_DEFAULT_FORMAT
from datetime import datetime

__author__ = 'Yeter Çatıkkaş'


class TestCase(BaseTestCase):
    """
    Personel atama iş akışını test eder.
    Veritabanına atama ve hizmet kayıtları nesnelerinin kaydedilip kaydedilmediği test eder.
    Eksik bilgileri düzenlenen personelin bilgilerinin, personele kaydedilip kaydedilmediği test edilir.
    Sunucudan dönen responseların doğruluğu test edilir.

    """
    def test_personel_atama(self):
        # personel_isleri_1 kullanıcısı seçilir.
        user = User.objects.get(username="personel_isleri_1")
        # Kullanıcıya giriş yaptırılıp, personel seçilir.
        self.prepare_client('/personel_atama', user=user)
        self.client.post(id="Zln6SwS3pRmEQlhIdasQlGddvie",
                         param="personel_id",
                         )
        # Önceki atamaların sayıları
        onceki_atama_sayilari = Atama.objects.filter(personel_id="Zln6SwS3pRmEQlhIdasQlGddvie").count()

        # Birim seçmeden ilerleme işlemi denenir.
        form = {'birim_id': None,
                'kaydet': 1,
                'iptal': None}

        # Personelin birim bilgileri gönderilir.
        resp = self.client.post(form=form, cmd='ileri')

        assert resp.json['reload_cmd'] == 'hatali_birim'

        # Kadro durumu uygun olmayan birim seçimi denenir.
        form = {'birim_id': "PNrGNyS35dmw9WHKPyl9Er0CiWN",
                'kaydet': 1,
                'iptal': None}

        # Personelin birim bilgileri gönderilir.
        resp = self.client.post(form=form, cmd='ileri')

        assert resp.json['reload_cmd'] == 'hatali_birim'

        # Kadro durumu uygun bir birim seçilir.
        form = {'birim_id': "BDJqrujKVKLOq7Gd33C34VwhsFo",
                'kaydet': 1,
                'iptal': None}

        self.client.post(form=form, cmd='ileri')

        form = {'atama_aciklama': "YENİDEN ATAMA",
                'durum': "WlbWjbkcp3sVYjx0CXK51fapvFG",
                'goreve_baslama_aciklama': "YENİDEN ATAMA",
                'goreve_baslama_tarihi': "27.10.2016",
                'ibraz_tarihi': "05.10.2016",
                'kadro': "5WxmRnIScmht7J43LOhqgfKKLVG",
                'kurum_onay_tarihi': "27.10.2016",
                'nereden': 6,
                'kaydet': 1,
                'iptal': 'null'

                }
        # Personelin atama bilgileri doldurulur ve kaydedilir.
        resp = self.client.post(form=form, cmd='kaydet')

        sonraki_atama_sayilari = Atama.objects.filter(personel_id="Zln6SwS3pRmEQlhIdasQlGddvie").count()

        # Atamanın kaydedilip kaydedilmediği test edilir.
        assert sonraki_atama_sayilari == onceki_atama_sayilari + 1

        # İş akışı adımının doğruluğu test edilir.
        assert resp.json['forms']['schema']['title'] == "Devam Etmek İstediğiniz İşlemi Seçiniz"

        # Personel bilgileri hitap ile eşleştirilir.
        resp = self.client.post(cmd="hitap_getir", form={'hitap': 1, 'bitir': 'null'})

        # Sunucudan dönen cevapta bilgi mesajının içereği kontrol edilir.
        assert "Personel için hitap bilgileri Hitap sunucusu ile eşleştirilemedi" in resp.json['msgbox']['msg']

        HizmetKayitlari.objects.get(self.client.current.task_data['h_k']).delete()
        # İş akışı tekrardan başlatılır.
        self.client.set_path('/personel_atama')
        self.client.post(id="Zln6SwS3pRmEQlhIdasQlGddvie",
                         model="Atama",
                         param="personel_id",
                         wf="personel_atama",
                         filters={'personel_id': {'values': ["Zln6SwS3pRmEQlhIdasQlGddvie"],
                                                         'type': "check"}})

        # Personelin eksik bilgileri düzeltilir.
        resp = self.client.post(
            form={'duzenle': 1,
                  'atama_yap': 'null',
                  'gecmis_atamalarim': 'null'},
            cmd="duzenle")
        assert resp.json['forms']['schema']['title'] == "Personel Bilgileri"

        personel = Personel.objects.get("Zln6SwS3pRmEQlhIdasQlGddvie")
        # Personelin önceki branşı
        personelin_onceki_bransi = personel.brans

        resp.json['forms']['model']['brans'] = "Fen Bilimleri"
        resp.json['forms']['model']['kaydet'] = 1
        for key in resp.json['forms']['model'].keys():
            if key[-7:] == "_tarihi" or key[-7:] == "_suresi":
                date = resp.json['forms']['model'][key]
                if date:
                    resp.json['forms']['model'][key] = datetime.strptime(
                        date, "%Y-%m-%dT%H:%M:%SZ").strftime(
                        DATE_DEFAULT_FORMAT)
                else:
                    resp.json['forms']['model'][key] = datetime.now().strftime(DATE_DEFAULT_FORMAT)

        # Eksik bilgiler kaydedilir.
        self.client.post(form=resp.json['forms']['model'], cmd="kaydet")

        # Personelin değiştirilen branşı
        personelin_sonraki_bransi = Personel.objects.get("Zln6SwS3pRmEQlhIdasQlGddvie").brans
        # Değiştirilen personel bilgilerinin kaydedilip kaydedilmediği test edilir.
        assert personelin_sonraki_bransi != personelin_onceki_bransi

        # Teste yapılan değişikler geri alınır.
        son_atama = personel.atama
        son_atama.kadro.durum = 2
        son_atama.kadro.save()
        son_atama.delete()
        personel.brans = personelin_onceki_bransi
        personel.save()








