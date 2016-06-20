# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from ulakbus.models import OgrenciDersi, Sinav
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import User


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_okutman_not_girisi(self):
        """
        Okutman not girişi iş akışının ilk iki adımında ders şubesi ve sınav seçilir.

        Seçilen ders ve seçilen sınav ait notlar okutman tarafından onaylanmışsa;

        Dönen cevapta ``Notlar Onaylandı`` başlığı olup olmadığını test eder.


        ``Notlar Onaylandı`` başlığı var ise;

        Seçilen ders şubesine ait derslere kayıtlı öğrencilerin ad, soyad bilgisi ile
        sunucudan dönen öğrenci kayıt listesinin ad, soyad bilgisinin eşitliği test edilir.

        Kullanıcı, ders seçim ya da sınav seçim ekranına dönerek sınav ve ders
        seçebilir.


        ``Önizleme`` başlığı var ise;

        Seçilen ders ve seçilen sınav ait notlar okutman tarafından onaylanmamıştır.

        Seçilen ders şubesine ait derslere kayıtlı öğrencilerin ad, soyad bilgisi ile
        sunucudan dönen öğrenci kayıt listesinin ad, soyad bilgisinin  eşitliği test edilir.

        Notlar düzenlenebilir, onaylanabilir, ders seçim ekranına ya da sınav seçim
        ekranına dönülebilir.

        Notlar onaylandıktan sonra dönen cevapta hocalara bilgilendirme mesajı içeren
        ``Notlar Kaydedildi`` olup olmadığını test eder.

        Ders onaylanmadan önceki öğrenci sayısı ile ders onaylandıktan sonraki
        öğrenci sayısının eşitliği test edilir.

        İş akışı tekrar başlatılıp onaylanan ders  ve onaylanan sınav tekrardan seçilir
        ve gelen mesaj başlığında `Notlar Kaydedildi`` olup olmadığını test eder.

        """

        # ogretim_uyesi_1 kullanıcısı seçilir.
        usr = User.objects.get('P2ir7Jns7xdmjh1lazZeSNbRBEn')
        time.sleep(1)

        # Kullanıcıya login yaptırılır.
        self.prepare_client('/okutman_not_girisi', user=usr)
        self.client.post()

        # Ders şubesi seçilir.
        self.client.post(cmd='Ders Şubesi Seçin',
                         form=dict(sube='PRGgozMfVXSrAqyO2aMnjS6aBQo', sec=1))
        # Seçilen şubeye ait sınav seçilir.
        resp = self.client.post(cmd='Sınav Seçin',
                                form=dict(sinav='L1gyNxQ39rGpAvdA0zYEEpAdslh', sec=1))

        assert resp.json['msgbox']['title'] == 'Notlar Onaylandı'

        # Veritabanından çekilen öğrenci bilgisi ile sunucudan gelen öğrenci bilgisi
        # karşılaştırılarak test edilir.
        for i in range(0, len(resp.json['object']['fields'])):
            ogrenci_ders = OgrenciDersi.objects.filter(sube_id='PRGgozMfVXSrAqyO2aMnjS6aBQo')[i]
            ogrenci_ad = "%s %s" % (ogrenci_ders.ogrenci_program.ogrenci.ad,
                                    ogrenci_ders.ogrenci_program.ogrenci.soyad)
            assert ogrenci_ad == resp.json['object']['fields'][i]['Adı Soyadı']

        # Sınav seçim ekranına geri döner
        self.client.post(cmd='ders_sec',
                         form=dict(sinav_secim=1, ders_secim='null'),
                         flow='sinav_secim_adimina_don')

        resp = self.client.post(cmd='Sınav Seçin',
                                form=dict(sinav='IvXH1cqyYoHznv0iRV4FjLvXWwz', sec=1))

        # Dersler okutman tarafından onaylanmamışsa;
        assert resp.json['forms']['schema']['properties']['kaydet']['title'] == 'Önizleme'
        assert 'inline_edit' in resp.json['forms']

        # Veritabanından çekilen öğrenci bilgisi ile sıunucudan gelen öğrenci bilgisi
        # karşılaştırılarak test edilir.
        for i in range(0, len(resp.json['forms']['model']['Ogrenciler'])):
            ogrenci_ders = OgrenciDersi.objects.filter(sube_id='PRGgozMfVXSrAqyO2aMnjS6aBQo')[i]
            ogrenci_ad = "%s %s" % (ogrenci_ders.ogrenci_program.ogrenci.ad,
                                    ogrenci_ders.ogrenci_program.ogrenci.soyad)
            assert ogrenci_ad == resp.json['forms']['model']['Ogrenciler'][i]['ad_soyad']

        # Öğrencilerin sayısı.
        num_of_ogrenci = len(resp.json['forms']['model']['Ogrenciler'])

        # Kayıtlar önizlenir.
        self.client.post(cmd='not_kontrol',
                         form=dict(Ogrenciler=resp.json['forms']['model']['Ogrenciler'], kaydet=1))

        # Sınav notları onaylanıp kaydedilir.
        # İş akışı bu adımdan sonra sona erer.
        resp = self.client.post(cmd='not_kaydet',
                                flow='end',
                                form=dict(kaydet_ve_sinav_sec='null', kaydet=1,
                                          kaydet_ve_ders_sec='null',
                                          not_duzenle='null', not_onay='null'))

        assert resp.json['msgbox']['title'] == 'Notlar Kaydedildi'

        # İş akışı tekrardan başlatılır.
        self.client.set_path('/okutman_not_girisi')
        self.client.post()

        # Ders şubesi seçilir.
        self.client.post(cmd='Ders Şubesi Seçin',
                         form=dict(sube='PRGgozMfVXSrAqyO2aMnjS6aBQo', sec=1))

        # Sınav seçilir.
        resp = self.client.post(cmd='Sınav Seçin',
                                form=dict(sinav='IvXH1cqyYoHznv0iRV4FjLvXWwz', sec=1))

        assert num_of_ogrenci == len(resp.json['object']['fields'])
        assert resp.json['msgbox']['title'] == 'Notlar Onaylandı'

        # Ilgili Sinav tekrardan degerlendirilebilir
        sinav = Sinav.objects.get('IvXH1cqyYoHznv0iRV4FjLvXWwz')
        sinav.degerlendirme = False
        sinav.save()

