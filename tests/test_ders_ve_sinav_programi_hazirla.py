# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.db.adapter.db_riak import BlockSave
from ulakbus.models import User, DersEtkinligi, SinavEtkinligi, Donem
from zengine.lib.test_utils import BaseTestCase
import time


class TestCase(BaseTestCase):

    def test_ders_programi_yap(self):

        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        unit = usr.role_set[0].role.unit()
        published_false_count = DersEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()

        self.prepare_client("/ders_programi_hazirla", user=usr)
        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmamış Ders Programı Var!"

        for i in range(2):

            self.client.post(cmd='incele')

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

            resp = self.client.post(form={'tamamla': 1})
            assert 'incele' and 'yayinla' in resp.json['forms']['model'].keys()

            self.client.post(cmd='incele')

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

            resp = self.client.post(form={'tamamla': 1})

        resp = self.client.post(cmd='bitir')

        assert resp.json['msgbox']['title'] == "Ders Programı Yayınlandı!"

        time.sleep(1)

        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmış Ders Programı Var!"

        published_true = DersEtkinligi.objects.filter(bolum=unit, published=True, donem=Donem.guncel_donem())

        assert published_false_count == len(published_true)

        for de in published_true:
            de.published = False
            de.save()

        time.sleep(1)

        assert published_false_count == DersEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()

    def test_sinav_programi_yap(self):
        usr = User.objects.get(username='ders_programi_koordinatoru_1')
        unit = usr.role_set[0].role.unit()
        published_false_count = SinavEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()

        self.prepare_client('/sinav_programi_hazirla', user=usr)
        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmamış Sınav Programı Var!"

        for i in range(2):

            self.client.post(cmd='incele')

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

            resp = self.client.post(form={'tamamla': 1})
            assert 'incele' and 'yayinla' in resp.json['forms']['model'].keys()

            self.client.post(cmd='incele')

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

            resp = self.client.post(form={'tamamla': 1})

        resp = self.client.post(cmd='bitir')

        assert resp.json['msgbox']['title'] == "Sınav Programı Yayınlandı!"

        time.sleep(1)

        resp = self.client.post()

        assert resp.json['msgbox']['title'] == "Yayınlanmış Sınav Programı Var!"

        published_true = SinavEtkinligi.objects.filter(bolum=unit, published=True, donem=Donem.guncel_donem())

        assert published_false_count == len(published_true)

        for se in published_true:
            se.published = False
            se.save()

        time.sleep(1)

        assert published_false_count == SinavEtkinligi.objects.filter(bolum=unit, published=False, donem=Donem.guncel_donem()).count()
