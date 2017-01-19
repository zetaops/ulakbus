# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Ceza
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import Personel


class TestCase(BaseTestCase):

    def test_idari_cezalar_takibi(self):
        personel_id = "OI3vq7rWIaTdSNUj4KwSBpeHMrc"
        personel = Personel.objects.get(personel_id)

        self.prepare_client('/idari_cezalar_takibi', username='personel_isleri_1')
        self.client.post(id=personel_id, model="Ceza", param="personel_id", wf="idari_cezalar_takibi")


        ceza_sayisi = Ceza.objects.filter(personel = personel).count()

        # Yeni Ceza Ekleme

        self.client.post(form={"add": 1}, cmd='add_edit_form')
        resp = self.client.post(form={"iptal": 1}, cmd='iptal')
        assert resp.json['forms']['schema']['title'] == 'İdari Cezalar'
        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi

        resp = self.client.post(form={"add": 1}, cmd='add_edit_form')

        assert resp.json['forms']['schema']['title'] == 'İdari Ceza'

        yeni_idari_ceza_form = {'acilis_tarihi': "17.01.2017",
            'baslama_tarihi': "17.01.2017",
            'bitis_tarihi': "18.01.2017",
            'dosya_sira_no': "12345",
            'ihbar_sikayet_suc_ogrenildigi_tarih': "10.01.2017",
            'kararin_teblig_tarihi': "19.01.2017",
            'dusunceler': "Dusunce Denemesi",
            'kaydet': 1}

        resp = self.client.post(form=yeni_idari_ceza_form)
        assert resp.json['msgbox']['title'] == "İdari Ceza Oluşturuldu"
        assert yeni_idari_ceza_form['dosya_sira_no'] in resp.json['msgbox']['msg']
        assert 'oluşturuldu' in resp.json['msgbox']['msg']

        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi + 1

        ceza_object = Ceza.objects.filter(personel=personel, dosya_sira_no='12345')[0]

        # Ceza Bilgilerini Düzenleme

        self.client.post(id=personel_id, model="Ceza", param="personel_id",
                         object_id=ceza_object.key, wf="idari_cezalar_takibi",
                         cmd="add_edit_form")

        resp = self.client.post(form={"iptal": 1}, cmd='iptal')
        assert resp.json['forms']['schema']['title'] == 'İdari Cezalar'
        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi + 1

        yeni_idari_ceza_form['dusunceler'] = "Deneme Dusuncesi"
        yeni_idari_ceza_form['object_key'] = ceza_object.key

        resp = self.client.post(id=personel_id, model="Ceza", param="personel_id",
                                object_id=ceza_object.key, wf="idari_cezalar_takibi",
                                cmd="add_edit_form")

        assert resp.json['forms']['schema']['title'] == 'İdari Ceza'
        assert resp.json['forms']['model']['dusunceler'] == 'Dusunce Denemesi'

        resp = self.client.post(cmd = 'add_edit_form',
                                form=yeni_idari_ceza_form,
                                model="Ceza",
                                wf="idari_cezalar_takibi")

        assert resp.json['msgbox']['title'] == "Değişiklikleriniz Kaydedildi"
        assert personel.__unicode__() in resp.json['msgbox']['msg']
        assert 'kaydedildi' in resp.json['msgbox']['msg']

        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi + 1

        # Ceza Bilgilerini Görüntüleme

        resp = self.client.post(id=personel_id, model="Ceza", param="personel_id",
                                object_id=ceza_object.key, wf="idari_cezalar_takibi",
                                cmd="goruntule")

        assert personel.__unicode__() and ceza_object.dosya_sira_no in resp.json['object_title']
        assert 'Deneme Dusuncesi' in resp.json['object'].values()
        assert resp.json['object']['Dosya No'] == ceza_object.dosya_sira_no

        resp = self.client.post(form={"tamam": 1}, cmd='iptal')

        assert resp.json['forms']['schema']['title'] == 'İdari Cezalar'
        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi + 1

        # Ceza Silme

        self.client.post(id=personel_id, model="Ceza", param="personel_id",
                         object_id=ceza_object.key, wf="idari_cezalar_takibi",
                         cmd="delete")

        resp = self.client.post(form={"hayir": 1}, cmd='iptal')
        assert resp.json['forms']['schema']['title'] == 'İdari Cezalar'
        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi + 1

        resp = self.client.post(id=personel_id, model="Ceza", param="personel_id",
                                object_id=ceza_object.key, wf="idari_cezalar_takibi",
                                cmd="delete")

        assert resp.json['forms']['schema']['title'] == "İdari Ceza Silme İşlemi"
        assert personel.ad in resp.json['forms']['form'][0]['helpvalue']
        assert yeni_idari_ceza_form['dosya_sira_no'] in resp.json['forms']['form'][0]['helpvalue']

        resp = self.client.post(form={"evet": 1}, cmd='delete')
        resp.json['msgbox']['title'] = "Silme İşlemi Başarılı"
        assert personel.__unicode__() in resp.json['msgbox']['msg']
        assert yeni_idari_ceza_form['dosya_sira_no'] in resp.json['msgbox']['msg']
        assert 'silindi' in resp.json['msgbox']['msg']
        assert Ceza.objects.filter(personel=personel).count() == ceza_sayisi

        ceza_object.blocking_delete()