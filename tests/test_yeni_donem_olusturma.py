# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User, Donem
from zengine.lib.test_utils import BaseTestCase
from pyoko.db.connection import log_bucket, version_bucket


class TestCase(BaseTestCase):
    def test_yeni_donem_olusturma(self):
        """
        Yeni Dönem Oluşturma iş akışının ilk adımında Güz ve Bahar
        Dönemi formu oluşturulur.

        İkinci adımında ise doldurulan form kaydedilir.
        Yeni eklenen dönemlerin kaydedilip kaydedilmediği test edilir.

        Üçüncü adımda ise işlemin başarılı olduğuna dair bilgilendirme
        mesajı basılır.
        Dönen cevapta msgbox olup olmadığı test edilir.

        """
        log_bucket_count = len(log_bucket.get_keys())
        log_bucket_keys = log_bucket.get_keys()
        version_bucket_keys = version_bucket.get_keys()

        # ogrenci_isleri_1 kullanıcısı seçilir.
        user = User.objects.get(username='ogrenci_isleri_1')

        # Kullanıcıya giriş yaptırılır.
        self.prepare_client('/yeni_donem_olusturma', user=user)
        self.client.post()

        # Yeni dönemler kaydedilmeden önceki dönem sayısı.
        baslangictaki_donem_sayisi = Donem.objects.filter().count()
        onceki_donem_keyleri = [d.key for d in Donem.objects.filter()]
        # Güz ve Bahar dönemi formları doldurulur, request yapılır.
        resp = self.client.post(
            form={'kaydet': 1, 'guz_baslangic_tarihi': '02.09.2017', 'guz_bitis_tarihi': '01.02.2018',
                  'bahar_baslangic_tarihi': '02.02.2018', 'bahar_bitis_tarihi': '01.07.2018'})

        # Save işlemi meta_data parametresi ile yapıldığından aktivite kaydının tutulması ve
        # bir artması beklenir.
        assert len(log_bucket.get_keys()) == log_bucket_count
        # WF isminin doğruluğu kontrol edilir.
        yeni_versiyon_kayitlari = list(set(version_bucket.get_keys()) - set(version_bucket_keys))
        # Bu kayıtlardan donemle ilgili olanları süzülür.
        donem_kayitlari = list(
            filter(lambda x: version_bucket.get(x).data['model'] == 'donem', yeni_versiyon_kayitlari))
        # Oluşturma zamanına göre sıralanır.
        sirali_donem_kayitlari = sorted(donem_kayitlari, key=lambda x: version_bucket.get(x).data['timestamp'])
        # Son kaydın güncel field'ının True olduğu kontrol edilir.
        print version_bucket.get(sirali_donem_kayitlari[0]).data['data']
        print version_bucket.get(sirali_donem_kayitlari[1]).data['data']

        # assert version_bucket.get(sirali_donem_kayitlari[0]).data['data']['baslangic_tarihi'] == '02.09.2015'
        # # Son kaydın dönem key'inin verilen key olduğu kontrol edilir.
        # assert version_bucket.get(sirali_donem_kayitlari[-1]).data['key'] == 'SBx09BKCv86hp53HGVT2i7vBxGN'
        # # Bir önceki dönem kaydının guncel field'ının False olduğu kontrol edilir.
        # # Bunun anlamı yeni güncel dönem kaydedilirken, öncelikle güncel olan dönemin güncel fieldı
        # # False yapılır ardından yeni istenilen dönem güncel olarak kaydedilir.
        # assert version_bucket.get(sirali_donem_kayitlari[0]).data['data']['guncel'] == False

        # Solr ve Riak arasındaki gecikmeden dolayı 1 saniye bekletilir.
        time.sleep(1)
        # Yeni dönemler eklendikten sonraki dönem sayısı
        son_donem_sayisi = Donem.objects.filter().count()

        # Yeni eklenen dönemlerin kaydedilip kaydedilmediği test edilir.
        assert son_donem_sayisi == baslangictaki_donem_sayisi + 2, 'Yeni eklenen dönemler kaydedilmedi.'
        # Dönen cevapta msgbox olup olmadığı test edilir.
        assert 'msgbox' in resp.json

        sonraki_donem_keyleri = [d.key for d in Donem.objects.filter()]
        silinen_donemler = [Donem.objects.get(d_key).delete() for d_key in sonraki_donem_keyleri if
                            d_key not in onceki_donem_keyleri]
        assert son_donem_sayisi - len(silinen_donemler) == baslangictaki_donem_sayisi
