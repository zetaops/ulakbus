# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import FormData
from ulakbus.models.auth import User
from zengine.lib.test_utils import BaseTestCase

class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_izin_basvuru(self):
        """
        İzin Başvuru iş akışı testinin ilk yolunda izin başvuru
        formu doldurulur.
        Form Data model nesnesinin kaydedilip test edilir.

        İzin Başvuru iş akışı testinin ikinci yolunda izin başvurusunda
        bulunan personelin izni kaydedilir.
        Bilgilendirme mesajı basılır.

        """
        # Kullanıcı seçilir.
        user = User.objects.get(username='personel_isleri_1')

        # Kullanıcıya login yaptırılır ve iş akışı başlatılır.
        self.prepare_client('/izin_basvuru', user=user)
        resp = self.client.post()

        form = {'izin_adres': "Urla", 'izin_turu': 2, 'izin_ait_yil': 2016, 'izin_baslangic': "15.05.2016",
                'izin_bitis': "20.05.2016", 'ileri': 1}

        # Giriş yapan personel kullanıcısına ait Form Data sayısı.
        count_of_form_data = FormData.objects.filter(user=user).count()

        if self.client.current.task_data['cmd'] == 'izin_basvuru_formu_goster':

            # İzin başvuru formu doldurulur ve kaydedilir.
            self.client.post(form=form)

            # Notification  mesajının  gönderilmesi için 1 saniye beklenir.
            time.sleep(1)

            # Giriş yapan personel kullanıcısına ait Form Data sayısı
            num_of_form_data = FormData.objects.filter(user=user).count()

            assert num_of_form_data == count_of_form_data + 1

            token, user = self.get_user_token('personel_isleri_2')

            # Kullanıcıya login yaptırılır, iş akışı başlatılır.
            self.prepare_client('/izin_basvuru', user=user, token=token)
            resp = self.client.post()
            form = {'ileri': 1, 'izin_adres': "Urla", 'izin_ait_yil': 2016, 'izin_baslangic': "15.05.2016",
                    'izin_bitis': "20.05.2016",
                    'izin_turu': 2, 'kalan_izin': 15, 'personel_ad_soyad': '',
                    'personel_birim': "COĞRAFYA ÖĞRETMENLİĞİ PR.",
                    'personel_gorev': "Memur", 'personel_sicil_no': 124, 'toplam_izin_gun': 5, 'toplam_kalan_izin': 15,
                    'yol_izni': False}
            self.client.post(form=form)

        else:
            assert 'msgbox' in resp.json
