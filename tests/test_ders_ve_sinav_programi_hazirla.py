# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.db.adapter.db_riak import BlockSave
from ulakbus.models import User, DersEtkinligi, SinavEtkinligi, Donem, Room
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):

    def test_ders_programi_yap(self):

        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        unit = usr.role_user_set[0].role.unit()
        ders_etkinligi = DersEtkinligi.objects.filter(bolum=unit, donem=Donem.guncel_donem())
        published_true = ders_etkinligi.filter(published=True)
        with BlockSave(DersEtkinligi, query_dict={'published': False}):
            for pt in published_true:
                pt.published = False
                pt.save()
        published_false_count = DersEtkinligi.objects.filter(bolum=unit, donem=Donem.guncel_donem(),
                                                             published=False).count()

        self.prepare_client("/ders_programi_hazirla", user=usr)
        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmamış Program Var!"

        self.client.post(form={'devam': 1})

        self.client.post(cmd='incele')

        for i in range(2):

            if i == 0:
                # Derslik Arama Kayit Yok
                ara_form = {'arama_button': 1,
                            'arama_sec': 1,
                            'arama_text': "C4034"}
                title = "Kayıt Bulunamadı"
            else:
                # Ogretim Elemani Arama Kayit Yok
                ara_form = {'arama_button': 1,
                            'arama_sec': 2,
                            'arama_text': "Baba Zula"}
                title = "Kayıt Bulunamadı"

            resp = self.client.post(form=ara_form)
            assert resp.json['msgbox']['title'] == title

            self.client.post(form={'devam': 1})

            if i == 0:
                # Derslik Arama Kayit Var
                ara_form = {'arama_button': 1,
                            'arama_sec': 1,
                            'arama_text': "C50610"}
                title = "C50610 C608 - CAD Laboratuarları 38 - Detaylı Zaman Tablosu"

            else:
                # Ogretim Elemani Arama Kayit Var
                ara_form = {'arama_button': 1,
                            'arama_sec': 2,
                            'arama_text': "İsmet Tarhan"}

                title = "İsmet Tarhan - Detaylı Zaman Tablosu"

            resp = self.client.post(form=ara_form)
            assert resp.json['objects'][1]['title'] == title

            self.client.post(form={'tamamla': 1})

        resp = self.client.post(cmd='vazgec')

        assert 'incele' and 'yayinla' in resp.json['forms']['model'].keys()

        resp = self.client.post(cmd='bitir')

        assert resp.json['msgbox']['title'] == "Program Yayınlandı!"

        time.sleep(1)

        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmış Program Var!"

        published_true = DersEtkinligi.objects.filter(bolum=unit, published=True, donem=Donem.guncel_donem())

        assert published_false_count == len(published_true)

        self.client.set_path("/derslik_ders_programlari")
        resp = self.client.post()
        derslikler = [etkinlik.room for etkinlik in published_true]
        assert len(resp.json['forms']['form'][2]['titleMap']) == len(derslikler)
        resp = self.client.post(form={"ileri": 1, "derslik": "3rPQ4bB2lDtxdCE41RBoNqZM19f"})
        num_of_ders_etkinlikleri = DersEtkinligi.objects.filter(room_id="3rPQ4bB2lDtxdCE41RBoNqZM19f", published=True,
                                                                donem=Donem.guncel_donem())
        count_of_ders_etkinlikleri = 0
        for i in range(1, len(resp.json['objects'])):
            for day in resp.json['objects'][i]['fields']:
                if resp.json['objects'][i]['fields'][day]:
                    count_of_ders_etkinlikleri += 1
        assert len(num_of_ders_etkinlikleri) == count_of_ders_etkinlikleri
        with BlockSave(DersEtkinligi, query_dict={'published': False}):
            for de in published_true:
                de.published = False
                de.save()

        assert published_false_count == DersEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()

    def test_sinav_programi_yap(self):
        """
        Derslik Sınav Programları iş akışı aşağıdaki adımlardan oluşur.

        İlk adımda sınav etkinlikleri kontrol edilir.
        Yayınlanlanmamış sınav etkinlikleri varsa;
        Bilgi ver wf adımına geçer. Bu adımda yayınlanmamış sınavların
        olduğuna dair bilgi mesajı ekrana basılır.

        İlk adımda derslik seçilir.
        Veritabanından çekilen derslik sayısı ile sunucudan dönen derslik sayısı karşılaştırılıp test edilir.

        İkinci adımda seçilen dersliğe ait sınav programı getirilir.
        Veritabanından çekilen sınav etkinlikleri sayısı ile sunucudan dönen sınav etkinlikleri sayısı
        karşılaştırılıp test edilir.

        """
        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        unit = usr.role_user_set[0].role.unit()
        sinav_etkinligi = SinavEtkinligi.objects.filter(bolum=unit, donem=Donem.guncel_donem())
        published_true = sinav_etkinligi.filter(published=True)
        with BlockSave(SinavEtkinligi, query_dict={'published': False}):
            for pt in published_true:
                pt.published = False
                pt.save()

        published_false_count = SinavEtkinligi.objects.filter(bolum=unit, donem=Donem.guncel_donem(),
                                                              published=False).count()

        self.prepare_client('/sinav_programi_hazirla', user=usr)
        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmamış Program Var!"

        self.client.set_path("/derslik_sinav_programlari")
        resp = self.client.post()
        assert "msgbox" in resp.json

        self.client.set_path('/sinav_programi_hazirla')
        self.client.post()

        self.client.post(form={'devam': 1})

        self.client.post(cmd='incele')

        for i in range(2):

            if i == 0:
                # Derslik Arama Kayit Yok
                ara_form = {'arama_button': 1,
                            'arama_sec': 1,
                            'arama_text': "C4034"}
                title = "Kayıt Bulunamadı"
            else:
                # Ogretim Elemani Arama Kayit Yok
                ara_form = {'arama_button': 1,
                            'arama_sec': 2,
                            'arama_text': "Baba Zula"}
                title = "Kayıt Bulunamadı"

            resp = self.client.post(form=ara_form)
            assert resp.json['msgbox']['title'] == title

            self.client.post(form={'devam': 1})

            if i == 0:
                # Derslik Arama Kayit Var
                ara_form = {'arama_button': 1,
                            'arama_sec': 1,
                            'arama_text': "M50616"}
                title = "M50616 C402 - Theatre 44 - Detaylı Zaman Tablosu"

            else:
                # Ogretim Elemani Arama Kayit Var
                ara_form = {'arama_button': 1,
                            'arama_sec': 2,
                            'arama_text': "İsmet Tarhan"}

                title = "İsmet Tarhan - Detaylı Zaman Tablosu"

            resp = self.client.post(form=ara_form)
            assert resp.json['objects'][1]['title'] == title

            self.client.post(form={'tamamla': 1})

        resp = self.client.post(cmd='vazgec')

        assert 'incele' and 'yayinla' in resp.json['forms']['model'].keys()

        resp = self.client.post(cmd='bitir')

        assert resp.json['msgbox']['title'] == "Program Yayınlandı!"

        time.sleep(1)

        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmış Program Var!"

        published_true = SinavEtkinligi.objects.filter(bolum=unit, published=True, donem=Donem.guncel_donem())

        assert published_false_count == len(published_true)

        self.client.set_path("derslik_sinav_programlari")
        resp = self.client.post()
        derslikler = [s_yerleri.room for s_etkinlik in published_true
                      for s_yerleri in s_etkinlik.SinavYerleri if s_etkinlik.SinavYerleri]
        assert len(derslikler) == len(resp.json['forms']['form'][2]['titleMap'])
        resp = self.client.post(form={"ileri": 1, "derslik": 'Jju1xbrWBsMoFb9fPyNpLnwPuW9'})
        room = Room.objects.get("Jju1xbrWBsMoFb9fPyNpLnwPuW9")
        num_of_sinav_etkinlikleri = [s for s in SinavEtkinligi.objects if room in s.SinavYerleri]
        count_of_sinav_etkinlikleri = 0
        for i in range(1, len(resp.json['objects'])):
            for day in resp.json['objects'][i]['fields']:
                if resp.json['objects'][i]['fields'][day]:
                    count_of_sinav_etkinlikleri += 1
        assert len(num_of_sinav_etkinlikleri) == count_of_sinav_etkinlikleri
        with BlockSave(SinavEtkinligi, query_dict={'published': False}):
            for se in published_true:
                se.published = False
                se.save()
        assert published_false_count == SinavEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()
