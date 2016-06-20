# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus.models import AkademikTakvim, Personel, Unit, User
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """Test Durumu

    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_list_add_delete_edit_with_models(self):
        """
        Crud iş akışına ait Personel modelini listele, ekleme
        ve silme işlemleriyle; AkademikTakvim modeli ise düzenle
        işlemi ile test eder. Crud iş akışına ait modelleri
        listele, ekleme,silme gibi işlemlerle test ederken aynı
        işlemleri(listele, ekleme,silme gibi) farklı modellerde
        test etmek gereksizdir.

        """

        # Veritabanından ulakbus adlı kullanıcı seçilir.
        usr = User.objects.get(username='ulakbus')

        # Crud iş akışını başlatır.
        self.prepare_client('/crud', user=usr)

        # Personel modeli ve varsayılan komut "list" ile sunucuya request yapılır.
        resp = self.client.post(model='Personel')
        assert 'objects' in resp.json

        # Mevcut kayıtların sayısını tutar.
        num_of_objects = len(Personel.objects.filter())

        # Yeni bir personel kaydı ekler, kayıtların listesini döndürür.
        self.client.post(model='Personel', cmd='add_edit_form')
        resp = self.client.post(model='Personel',
                                cmd='save::list',
                                form=dict(ad="Nuray ", tckn="12323121443", soyad='Söner'))

        # Eklenen kaydın, başlangıçtaki kayıtların sayısında
        # değişiklik yapıp yapmadığını test eder.
        assert num_of_objects + 1 == len(Personel.objects.filter())

        silenecek_personel = Personel.objects.get(resp.json['objects'][4]['key'])

        # İlk kaydı siliyor, kayıtların listesini döndürür.
        resp = self.client.post(model='Personel',
                                cmd='delete',
                                object_id=resp.json['objects'][4]['key'])
        time.sleep(1)

        # Mevcut kayıtların sayısının, başlangıçtaki kayıt
        # sayısına eşit olup olmadığını test eder.
        assert 'reload' in resp.json['client_cmd']

        silenecek_personel.deleted = False
        silenecek_personel.save()


        # AkademikTakvim modeli ve varsayılan komut 'list' ile sunucuya
        # request yapılır.
        resp = self.client.post(model='AkademikTakvim')

        # İlk kaydı düzenlemek için seçer.
        response = self.client.post(model='AkademikTakvim',
                                    cmd='add_edit_form',
                                    object_id=resp.json['objects'][1]['key'])
        # Kaydın key değeri.
        object_key = response.json['forms']['model']['object_key']
        # Birimin key değeri.
        unit_id = response.json['forms']['model']['birim_id']

        resp = self.client.post(model='Unit',
                                cmd='object_name',
                                object_id=unit_id)

        # Veritabanından kayıtlı nesne çekilir.
        objct = AkademikTakvim.objects.get(object_key)

        # Veritabanındaki kayıtlı akademik takvimin birim ismi ile sunucudan dönen
        # akademik takvimin birim ismi karşılaştırılıp test edilir.
        assert objct.birim.name in resp.json['object_name']

    def test_add_search_filter_select_list(self):
        """
        Crud iş akışına ait Personel modelini arama, ekleme ve
        filtreleme işlemleriyle, AkademikTakvim modelini is select list
        işlemiyle test eder.

        """

        # Veritabanından ulakbus adlı kullanıcı seçilir.
        usr = User.objects.get(username='ulakbus')

        # Crud iş akışını başlatır.
        self.prepare_client('/crud', user=usr)

        # crud iş akışı tekrardan başlatılır.
        self.client.set_path('/crud')
        self.client.post(model='Personel', cmd='list')

        # Query değerine göre personel kayıtlarını filtreler.
        resp = self.client.post(model='Personel', query="12345678")
        assert len(resp.json['objects']) - 1 == len(
            Personel.objects.filter(tckn__startswith='12345678'))

        # crud iş akışı tekrardan başlatılır.
        self.client.set_path('/crud')
        self.client.post(model='AkademikTakvim')

        # Queryset alanına rastgele girilir.
        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='jsghgahfsghfaghfhga')

        num_of_kayit = Unit.objects.filter(name='jsghgahfsghfaghfhga')

        # 0 değeri ise queryset alanına girilen değere ait herhangi
        # bir kayıt bulunamadığını gösterir.
        assert resp.json['objects'][0] == num_of_kayit.count()

        resp = self.client.post(model='Unit',
                                cmd='select_list')

        # -1 değeri ise queryset alanına herhangi bir değer girilmediğini gösterir.
        assert resp.json['objects'][0] == -1

        num_of_kayit = Unit.objects.filter(name='MOLEKÜLER BİYOLOJİ VE GENETİK BÖLÜMÜ')

        resp = self.client.post(model='Unit',
                                cmd='select_list',
                                query='MOLEKÜLER BİYOLOJİ VE GENETİK BÖLÜMÜ')

        # Queryset alanına girilen değere ait bir ya da birden fazla kayıt bulunduğunu gösterir.
        assert len(resp.json['objects']) == num_of_kayit.count()
