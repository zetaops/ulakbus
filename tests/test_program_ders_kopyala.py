# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from .base_test_case import BaseTestCase
import time
from ulakbus.models import User, Program, Ders, Donem
from datetime import date


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_program_ders_kopyala(self):
        """
        Program Ders Kopyalama wf test methodu.

        Program Ders Kopyalama iş akışının ilk adımında program seçilir.

        Seçilen öğrenciye ait veritabanından dönen program sayısı ile
        sunucudan dönen program sayısının eşitliği karşılaştırılıp test edilir.

        İş akışının ikinci adımında senato numarası girilir ve dersler kopyalanır.

        İş akışının üçüncü adımında programa ait dersler gösterilir ve değişiklik
        yapılması istenen derslerin seçilmesi beklenir. Sunucudan dönen ders sayısı
        ile veritabanında bulunan ders sayısının aynı olup olmadığı test edilir.

        İş akışının dördüncü adımında seçilen derslerde yapılan değişikliklerin
        veritabanına kaydedilip kaydedilmediği kontrol edilir.

        """

        # veritabanından test_user seçilir.
        usr = User.objects.get(username='test_user')

        # program_ders_kopyala workflowu çalıştırılır.
        self.prepare_client('/program_ders_kopyala', user=usr)
        resp = self.client.post()

        # veritabanındaki program sayısı çekilir.
        program_sayisi = Program.objects.filter().count()

        # Veritabanından çekilen program sayısı ile sunucudan dönen program sayısının
        # eşitliği karşılaştırılıp test edilir.
        assert program_sayisi == len(resp.json['forms']['form'][1]['titleMap'])

        # İlk program seçilir
        resp = self.client.post(form={'program': "Gvsgkf7JMgIHKBY6JAO4wFC5kc6", 'sec': 1})

        # Senato numarası girilir,
        resp = self.client.post(form={'kaydet': 1, 'senato_karar_no': "123"})

        program = Program.objects.get("Gvsgkf7JMgIHKBY6JAO4wFC5kc6")
        program_versiyon_sayisi = len(program.Version)
        senato_karar_no = program.Version[program_versiyon_sayisi - 1].senato_karar_no

        # "123" olarak girilen senato numarasının kaydedilip kaydedilmediği test edilir.
        assert senato_karar_no == '123'

        # "SEN123" olarak üretilmesi beklenen program versiyon numarası test edilir.
        assert program.Version[program_versiyon_sayisi - 1].no == "SEN" + senato_karar_no

        guncel_yil = date.today().year
        guncel_yil = str(guncel_yil)

        # Güncel yıla göre kopyalanmış ve seçilen programa ait dersler veritabanından çekilir.
        dersler = Ders.objects.filter(program=program, yil=guncel_yil)

        # Veritabanında bulunan dersler ile sunucudan dönen derslerin sayıları karşılaştırılır.
        assert len(dersler) == len(resp.json['forms']['model']['Dersler'])

        # Hiç ders seçilmemesi durumunda uyarı mesajı çıkması test edilir.
        resp = self.client.post(form={'duzenle': 1, 'Dersler': resp.json['forms']['model']['Dersler']})
        assert resp.json['forms']['schema']['title'] == 'Uyar\xc4\xb1 Mesaj\xc4\xb1'

        resp = self.client.post(form={'onayla': 'null', 'geri_don': 1}, flow="ders_tablo")

        # Tabloda gösterilen derslerden ilki seçilir.
        resp.json['forms']['model']['Dersler'][0]['secim'] = True
        resp.json['forms']['model']['Dersler'][1]['secim'] = True
        resp = self.client.post(form={'duzenle': 1, 'Dersler': resp.json['forms']['model']['Dersler']})

        # İlk formda dersin adı Embedded olarak değiştirilir.
        resp.json["forms"]["model"]["ad"] = "Embedded"
        form_bir_kontrol = resp.json["forms"]["model"]
        resp = self.client.post(form=form_bir_kontrol)

        key = resp.json["forms"]["model"]["object_key"]
        secilen_ders = Ders.objects.get(key)

        # İlk formda ders adı değişikliğinin veritabanında da yapılıp yapılmadığı kontrol edilir.
        assert secilen_ders.ad == "Embedded"

        # İkinci formda ders içeriği Math olarak değiştirilir.
        resp.json["forms"]["model"]["ders_icerigi"] = "Math"
        form_iki_kontrol = resp.json["forms"]["model"]

        key = resp.json["forms"]["model"]["object_key"]
        secilen_ders = Ders.objects.get(key)
        self.client.post(form=form_iki_kontrol)

        # İkinci formda ders içeriği değişikliğinin veritabanında da yapılıp yapılmadığı kontrol edilir.
        assert secilen_ders.ders_icerigi == "Math"

        # İkinci seçilen dersin ilk formuna tıklanır.
        resp = self.client.post(form=form_bir_kontrol)
        # İkinci seçilen dersin ikinci formuna tıklanır.
        resp = self.client.post(form=form_iki_kontrol)

        # Değişiklikler bittiğinde Tamamla butonuna basıldığında bitirip bitirmediği test edilir.  
        resp = self.client.post(form={'onayla': 1, 'geri_don': 'null'}, flow="personel_bilgilendir")
        assert resp.json['msgbox']['title'] == "Onay Mesajı"
