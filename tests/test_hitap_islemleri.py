# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import pytest
import time
from ulakbus.models import HizmetKurs, ObjectDoesNotExist
from zengine.lib.test_utils import BaseTestCase
from ulakbus.lib.cache import HitapPersonelGirisBilgileri


class TestCase(BaseTestCase):
    def test_hitap_islemleri(self):
        personel_id = "OI3vq7rWIaTdSNUj4KwSBpeHMrc"
        HizmetKurs.objects.filter(personel_id=personel_id)._clear()

        HitapPersonelGirisBilgileri(personel_id).delete()
        self.prepare_client('/hitap_islemleri', username='ulakbus')
        resp = self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                                wf="hitap_islemleri")
        assert resp.json['forms']['schema']['title'] == "Hitap Servisi Giriş Bilgileri"

        # Yanlış hitap kullanıcı adı veya şifre girilmesi kontrolü.
        resp = self.client.post(
            form={"hitap_k_adi": 'wrong_uname', "hitap_parola": 'wrong_pass', 'ilerle': 1})

        assert resp.json['msgbox']['title'] == "Hatalı Hitap Giriş Bilgileri"
        assert resp.json['forms']['schema']['title'] == "Hitap Servisi Giriş Bilgileri"

        # Doğru hitap kullanıcı adı veya şifre girilmesi kontrolü.
        resp = self.client.post(
            form={"hitap_k_adi": 'temp_uname', "hitap_parola": 'temp_pass', 'ilerle': 1})
        assert resp.json['forms']['schema']['title'] == "İşlem Seçeneği"
        # Doğrulanmış kullanıcı adı ve şifre cache'e koyulur.
        assert HitapPersonelGirisBilgileri(personel_id) is not None

        # Yeniden giriş yapılır ve hitap için kullanıcı adı ve şifre sormaması, cachede bulunan
        # bilgileri kullandığı kontrol edilir.
        self.prepare_client('/hitap_islemleri', username='ulakbus')
        resp = self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                                wf="hitap_islemleri")
        assert resp.json['forms']['schema']['title'] == "İşlem Seçeneği"

        # Hitap ile senkronize etme ekranı kontrolleri
        resp = self.client.post(form={"hitap_bilgileri": 1}, cmd='hitap_bilgileri',
                                model='HizmetKurs', wf='hitap_islemleri')
        assert resp.json['forms']['schema']['properties']['senkronize'][
                   'title'] == "Hitap İle Senkronize Et"
        assert resp.json['forms']['schema']['title'] == "Hitap Kurs Bilgileri"

        # Hitap ile senkronize etme servisinin çalışması
        resp = self.client.post(form={"senkronize": 1}, cmd='sync', model='HizmetKurs',
                                wf='hitap_islemleri')
        assert resp.json['msgbox']['title'] == "İşlem Başarılı"
        kayit_sayisi = HizmetKurs.objects.filter(personel_id=personel_id, sync=1).count()
        assert len(resp.json['objects']) == kayit_sayisi + 1

        self.prepare_client('/hitap_islemleri', username='ulakbus')
        self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                         wf="hitap_islemleri")
        self.client.post(form={"degisiklik": 1}, cmd='degisiklik', model='HizmetKurs',
                         wf='hitap_islemleri')

        updated_obj = HizmetKurs.objects.filter(personel_id=personel_id, sync=1)[0]
        main_key = updated_obj.key
        update_kayit = updated_obj.kayit_no
        updated_obj.key = ''
        new_obj = updated_obj.save()
        updated_obj = HizmetKurs.objects.get(main_key)
        new_obj.sync = None
        new_obj.kayit_no = None
        new_obj.save()
        deleted_obj = HizmetKurs.objects.filter(personel_id=personel_id, sync=1)[1]

        # Güncellenecek kayıt kaydetme işlemi sync ataması kontrolü
        self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                         object_id=updated_obj.key, wf="hitap_islemleri", cmd="save")

        updated_obj.reload()
        assert updated_obj.sync == 4

        # Yeni eklenecek kayıt kaydetme işlemi sync ataması kontrolü
        self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                         object_id=new_obj.key, wf="hitap_islemleri", cmd="save")

        new_obj.reload()
        assert new_obj.sync == 2

        # Silincek kayıt silme işlemi sync ataması kontrolü
        self.client.post(id=personel_id, model="HizmetKurs", param="personel_id",
                         object_id=deleted_obj.key, wf="hitap_islemleri", cmd="delete")

        deleted_obj.reload()
        assert deleted_obj.sync == 3
        time.sleep(1)

        # Yapılan değişikliklerin hitapa gönderilmesi kontrolü

        self.client.post(form={"gonder": 1}, id=personel_id, model="HizmetKurs",
                         param="personel_id",
                         wf="hitap_islemleri", cmd="gonder")

        with pytest.raises(ObjectDoesNotExist):
            deleted_obj.reload()

        new_obj.reload()
        updated_obj.reload()

        assert new_obj.kayit_no is not None
        assert new_obj.sync == 1
        assert updated_obj.kayit_no != update_kayit
        assert updated_obj.sync == 1
