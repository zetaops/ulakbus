# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, Sube, DersKatilimi
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.
    """

    def test_ders_katilim(self):
        """
        Ders katılımı iş akışının ilk adımda okutmanın kayıtlı olduğu şubelerden
        biri seçilir.
        Sunucudan dönen okutmanın kayıtlı olduğu şube sayısı ile veritabından çekilen
        okutmanın sayısı karşılaştırılıp test edilir.

        İş akışının ikinci adımında katılım formu doldurulur ve kontrol edilir.

        İş akışının üçüncü adımda katılım formu kaydedilir ya da geriye dönüp form tekrardan
        düzenlenir.
        Katılım formu kaydedilir ve katılım durumu değerinin kaydedilip kaydedilmediği test
        edilir.

        İş akışının son adımında bilgilendirme mesajı ekran basılır.

        """

        def get_okutman_key():
            """
            Okutman nesnesinin keyini bulur.

            Returns:
                Okutman nesnesinin keyini

            """

            return self.client.current.user.personel.okutman.key if self.client.current.user.personel.key \
                else self.client.current.user.harici_okutman.okutman.key

        # Verirabanından ogretim_uyesi_1 kullanıcısı seçilir.
        user = User.objects.get(username='ogretim_uyesi_1')

        # Kullanıcıya giriş yaptırılır.
        self.prepare_client('/ders_katilimi_giris', user=user)
        resp = self.client.post()

        # Okutmanın bağlı olduğu şubeler.
        sube_lst = Sube.objects.filter(okutman_id=get_okutman_key())

        # Sunucudan dönen cevapla veri tabanından çekilen şube sayıları karşılaştırılıp test edilir.
        assert len(sube_lst) == len(resp.json['forms']['form'][1]['titleMap'])

        # Şube seçilir.
        resp = self.client.post(form={'sube': "VgX4EFavEABkgaahcuxPyKbUog1", 'sec': 1})

        resp.json['forms']['model']['Ogrenciler'][0]['katilim_durumu'] = 80
        resp.json['forms']['model']['Ogrenciler'][0]['aciklama'] = 'Devamlı'

        sube_key = resp.json['forms']['model']['Ogrenciler'][0]['sube_key']
        ogrenci_key = resp.json['forms']['model']['Ogrenciler'][0]['ogrenci_key']

        # Katılım durumu formu doldurulur.
        resp = self.client.post(
            form={'onizleme': 1, 'cmd': 'kontrol', 'Ogrenciler': resp.json['forms']['model']['Ogrenciler']})

        ilk_ders_katilimi = DersKatilimi.objects.get(sube_id=sube_key, ogrenci_id=ogrenci_key)

        # Öğrenciye ait katılım formu kaydedilir.
        resp = self.client.post(form={'kaydet': 1, 'Ogrenciler': resp.json['forms']['model']['Ogrenciler']})

        son_ders_katilimi = DersKatilimi.objects.get(sube_id=sube_key, ogrenci_id=ogrenci_key)

        assert 'msgbox' in resp.json

        # Değiştirilen katılım durumunun kaydedilip kaydedilmediği test edilir.
        assert son_ders_katilimi.katilim_durumu != ilk_ders_katilimi.katilim_durumu \
               and son_ders_katilimi.katilim_durumu == 80
        son_ders_katilimi.katilim_durumu = 90
        son_ders_katilimi.save()
