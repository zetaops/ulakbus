# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User, Donem
from zengine.lib.test_utils import BaseTestCase


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
            form={'kaydet': 1, 'guz_baslangic_tarihi': '02.09.2015', 'guz_bitis_tarihi': '15.02.2016',
                  'bahar_baslangic_tarihi': '01.03.2016', 'bahar_bitis_tarihi': '17.06.2016'})

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
