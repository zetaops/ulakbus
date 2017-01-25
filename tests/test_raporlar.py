# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import *
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.translation import format_currency
from zengine.lib.utils import solr_to_year
from collections import defaultdict


class TestCase(BaseTestCase):

    def login_rapor(self, model_name):
        """
            Bütün raporları test ederken ulakbus kullanıcısı kullanılır.
            ilgili rapor çalıştırıl ve sonuç geri döndürülür.
        Args:
            model_name: Cağırılacak rapor modelinin ismi

        Returns: response

        """
        self.prepare_client('generic_reporter/', username='ulakbus')
        resp = self.client.post(cmd='show', model=model_name)

        return resp

    def test_cinsiyete_gore_ogrenci_sayilari(self):
        """
            Ogrenci cinsiyet sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir
        """

        ogrenci_cinsiyet = Ogrenci.objects.distinct_values_of('cinsiyet')

        kadin_ogrenci_sayisi = ogrenci_cinsiyet['2']
        erkek_ogrenci_sayisi = ogrenci_cinsiyet['1']

        resp = self.login_rapor(model_name='OgrenciByGender')

        assert resp.json['object'][u'Kadın'] == str(kadin_ogrenci_sayisi)
        assert resp.json['object'][u'Erkek'] == str(erkek_ogrenci_sayisi)

    def test_dogum_yerine_gore_ogrenci_sayilari(self):
        """
            Illere gore ogrenci sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir
        """

        ogrenci_dogum_yerleri_ve_sayilari = Ogrenci.objects.distinct_values_of('dogum_yeri')

        resp = self.login_rapor(model_name='OgrenciByBrithPlace')

        for dogum_yeri, sayisi in ogrenci_dogum_yerleri_ve_sayilari.items():
            assert resp.json['object'][dogum_yeri] == str(sayisi)

    def test_dogum_tarihine_gore_ogrenci_sayilari(self):
        """
            Dogum tarihi yillarina ait ogrenci sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir.
        """
        tarihler = defaultdict(lambda: 0)

        for val, num in Ogrenci.objects.distinct_values_of('dogum_tarihi').items():
            tarihler[solr_to_year(val)] += int(num)

        resp = self.login_rapor(model_name='OgrenciByBrithDate')

        for tarih, sayi in tarihler.items():
            assert resp.json['object'][tarih] == str(sayi)

    def test_ogrenci_harc_bilgileri(self):
        """
            Ogrenci harc miktarlarinin rapora dogru miktar da gelip gelmedigi
            kontrolu yapilir.
        """
        borc = Borc.objects.filter()
        ogrenci_ogretim_ucreti = format_currency(
            sum(borc.filter(sebep=1).values_list('miktar')), "TRY")
        ogrenci_yaz_okulu_ucreti = format_currency(
            sum(borc.filter(sebep=2).values_list('miktar')), "TRY")
        ogrenci_kimlik_ucreti = format_currency(
            sum(borc.filter(sebep=3).values_list('miktar')), "TRY")

        resp = self.login_rapor(model_name='OgrenciHarc')

        assert resp.json['object'][u'Kimlik Ücreti Borç'] == ogrenci_kimlik_ucreti
        assert resp.json['object'][u'Yaz Okulu Ücreti Borç'] == ogrenci_yaz_okulu_ucreti
        assert resp.json['object'][u'Öğretim Ücreti Borç'] == ogrenci_ogretim_ucreti

    def test_kapasitesine_gore_oda_sayilari(self):
        """
            Kapasiteye gore oda sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir.
        """

        oda_kapasiteleri_ve_sayilari = sorted(Room.objects.distinct_values_of('capacity').items())

        resp = self.login_rapor(model_name='RoomCapacities')

        assert len(oda_kapasiteleri_ve_sayilari) == len(resp.json['object']['fields'])

        i = 0
        for kapasite, sayi in oda_kapasiteleri_ve_sayilari:
            assert resp.json['object']['fields'][i]["Kapasite"] == str(kapasite)
            assert resp.json['object']['fields'][i]["Oda Sayısı"] == str(sayi)
            i += 1

    def test_cinsiyete_gore_personel_sayilari(self):
        """
            Personel cinsiyet sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir.
        """

        personel_cinsiyet = Personel.objects.distinct_values_of('cinsiyet')

        kadin_personel_sayisi = personel_cinsiyet['2']
        erkek_personel_sayisi = personel_cinsiyet['1']

        resp = self.login_rapor(model_name='PersonelByGender')

        assert resp.json['object'][u'Kadın'] == str(kadin_personel_sayisi)
        assert resp.json['object'][u'Erkek'] == str(erkek_personel_sayisi)

    def test_akademik_idari_personel_sayisi(self):
        """
            Akademik ve Idari personel sayilarinin rapora dogru sayilarda gelip gelmedigi
            kontrolu yapilir.
        """
        akademik_ve_idari_personel_sayilari = Personel.objects.distinct_values_of('personel_turu')

        akademik_personel_sayisi = akademik_ve_idari_personel_sayilari['1']
        idari_personel_sayisi =  akademik_ve_idari_personel_sayilari['2']

        resp = self.login_rapor(model_name='PersonelByAkademikIdari')

        assert resp.json['object'][u'Akademik'] == str(akademik_personel_sayisi)
        assert resp.json['object'][u'İdari'] == str(idari_personel_sayisi)

    def test_genel_kadro_durumlari(self):
        """
            İzinli ve Saklı durumuna sahip kadro durumlarının sayısı
            rapor olusturuldugunda doğru sayıda gelip, gelmediği kontrolü yapılır.
        """
        sakli_ve_izinli_kadro_sayilari = Kadro.objects.distinct_values_of('durum')

        sakli_kadro_sayisi = sakli_ve_izinli_kadro_sayilari['1']
        izinli_kadro_sayisi = sakli_ve_izinli_kadro_sayilari['2']

        resp = self.login_rapor(model_name='Kadrolar')

        assert resp.json['object'][u'Saklı'] == str(sakli_kadro_sayisi)
        assert resp.json['object'][u'İzinli'] == str(izinli_kadro_sayisi)

    def test_terfisi_tikanan_personel_listesi(self):
        """
            Terfisi tıkanan personel sayısının rapor olusturulurken
            dogru gelip gelmedigini kontrol eder.
        """
        terfisi_tikanan_personeller = Personel.objects.set_params(
            fq="{!frange l=0 u=0 incu=true}sub(gorev_ayligi_derece,kadro_derece)").filter(
            gorev_ayligi_kademe__gte=4)

        resp = self.login_rapor(model_name='TerfisiTikananPersonel')

        if 'fields' in resp.json['object']:
            assert len(resp.json['object']['fields']) == len(terfisi_tikanan_personeller)
        else:
            assert len(terfisi_tikanan_personeller) == 0

    def test_gorev_suresi_dolan_personel_listesi(self):
        """
            Görev süresi biten personellerin sayısının rapor olusturulurken
            dogru gelip gelmediğini kontrol eder.

        """

        simdi = datetime.date.today()
        bitis_tarihi = simdi + datetime.timedelta(days=120)

        gorev_suresi_dolan_personeller = Personel.objects.filter(
            gorev_suresi_bitis__lte=bitis_tarihi,
            personel_turu=1
        )

        resp = self.login_rapor(model_name='GorevSuresiBitenPersonel')

        if 'fields' in resp.json['object']:

            assert len(resp.json['object']['fields']) == len(gorev_suresi_dolan_personeller)
        else:
            assert len(gorev_suresi_dolan_personeller) == 0

