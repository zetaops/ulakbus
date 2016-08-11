# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


import time

from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.auth import User, Unit
from ulakbus.models.ogrenci import AKADEMIK_TAKVIM_ETKINLIKLERI, OgretimYili, Donem
from ulakbus.models.ogrenci import AkademikTakvim
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_academic_calendar(self):
        """
        Adalet Meslek Yüksekokulu Öğrencisi rolüne sahip ogrenci_1 adlı kullanıcı giriş yaptığında,
        xxxxxxxxxxxxxx keyine sahip rektörlüğe ait akademik takvimi görmesi beklenir.
        Çünkü bölümüne veya fakültesine ait bir akademik takvim tanımlanmamıştır.

        Bu iş akışı ilk adımda rektörlüğe ait akademik takvim kayıtlarını listeler.

        Veritabanından çekilen akademik takvim kayıtlarının sayısı ile sunucudan dönen akademik takvim
        kayıtlarının sayısı karşılastırılıp test edilir.

        Akademik takvim kaydının nesnelerinden biri seçilir, seçilen nesnenin etkinliği, başlangıcı ve
        bitişi sunucudan dönen etkinlik, başlangıç ve bitiş kayıtlarıyla karşılaştırılıp test edilir.

        ogrenci_1 adlı kullanıcıya çıkış yaptırılır.

        Kamu Hukuku Bölümü öğrencisi rolüne sahip ogrenci_2 adlı kullanıcı giriş yaptığında, xxxxxxxxxx keyine sahip
        Kamu Hukuku Bölümü akademik takvimi görmesi beklenir.Çünkü kendi bölümüne ait tanımlı akademik takvim vardır.

        Bu iş akışı ilk adımda eğitim fakültesine ait akademik takvim kayıtlarını listeler.

        Veritabanından çekilen akademik takvim kayıtlarının sayısı ile sunucudan dönen akademik takvim
        kayıtlarının sayısı karşılastırılıp test edilir.

        Akademik takvim kaydının nesnelerinden biri seçilir, seçilen nesnenin etkinliği, başlangıcı ve
        bitişi sunucudan dönen etkinlik, başlangıç ve bitiş kayıtlarıyla karşılaştırılır.

        """

        def get_akademik_takvim(unit, ogretim_yili):
            try:
                akademik_takvim = AkademikTakvim.objects.get(birim=unit, ogretim_yili=ogretim_yili)
                return akademik_takvim
            except ObjectDoesNotExist:
                parent_yoksis_no = unit.parent_unit_no
                birim = Unit.objects.get(yoksis_no=parent_yoksis_no)
                return get_akademik_takvim(birim, ogretim_yili)

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/akademik_takvim', username='ogrenci_1')
        resp = self.client.post()

        # Veritabınından ogrenci_1 adlı kullanıcı seçilir.
        user = User.objects.get(username='ogrenci_1')

        # Rol'ün kayıtlı olduğu birim getirilir.
        unit = user.role_set[0].role.unit

        ogretim_yili = OgretimYili.objects.get(yil=Donem.guncel_donem().baslangic_tarihi.year)

        # Birimin kayıtlı olduğu akademik takvim kayıtlarını getirir.
        akademik_takvim = get_akademik_takvim(unit, ogretim_yili)

        # Sunucudan dönen akademik takvim kayıtları ile veritabanından çekilen akademik kayıtları
        # karşılaştırılıp test edilir
        assert len(akademik_takvim.etkinlikler()) == len(resp.json['object']['fields'])

        # Akademik takvim kaydının nesnelerinden biri seçilir.
        takvim = akademik_takvim.etkinlikler()[4]
        # Takvim kaydının etkinliğini getirir.
        etkinlik = takvim.etkinlik

        assert dict(AKADEMIK_TAKVIM_ETKINLIKLERI).get(str(etkinlik), '') == \
               resp.json['object']['fields'][4][
                   'Etkinlik']
        assert takvim.baslangic.strftime('%d.%m.%Y') == resp.json['object']['fields'][4][
            'Başlangıç']
        assert takvim.bitis.strftime('%d.%m.%Y') == resp.json['object']['fields'][4][
            'Bitiş']

        # Kullanıcıya çıkış yaptırılır.
        self.client.set_path('/logout')
        self.client.post()

        # Veritabınından ogrenci_2 adlı kullanıcı seçilir.
        usr = User.objects.get(username='ogrenci_2')
        time.sleep(1)

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/akademik_takvim', user=usr)
        response = self.client.post()

        # Rol'ün kayıtlı olduğu birim getirilir.
        unit = usr.role_set[0].role.unit

        # Birimin kayıtlı olduğu akademik takvim kayıtını getirir.
        akademik_takvim = get_akademik_takvim(unit, ogretim_yili)

        # Sunucudan dönen akademik takvim kayıtları ile veritabanından çekilen akademik kayıtları
        # karşılaştırılıp test edilir.
        assert len(akademik_takvim.etkinlikler()) == len(response.json['object']['fields'])

        # Akademik takvim kaydının nesnelerinden biri seçilir.
        takvim = akademik_takvim.etkinlikler()[5]
        # Takvim kaydının etkinliğini getirir.
        etkinlik = takvim.etkinlik

        assert response.json['object']['fields'][5]['Etkinlik'] == dict(
            AKADEMIK_TAKVIM_ETKINLIKLERI).get(
            str(etkinlik), '')
        assert response.json['object']['fields'][5]['Başlangıç'] == takvim.baslangic.strftime(
            '%d.%m.%Y')
        assert response.json['object']['fields'][5]['Bitiş'] == takvim.bitis.strftime('%d.%m.%Y')
