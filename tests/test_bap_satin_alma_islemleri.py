# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time
from ulakbus.models import User, BAPTeklif, BAPButcePlani, BAPSatinAlma, BAPTeklifFiyatIsleme
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    BAP satın alma duyurularının listelenmesini ve duyurulara ait işlemlerin gerçekleştirilmesini sağlayan iş akışı testi. İş akışının doğru çalışması için her çalıştırıldığında BAPSatinAlma modeli resetlenmeli ve bap_proje.csv yeniden yüklenmelidir.

    """

    def test_bap_satin_alma_islemleri(self):
        # Durumu 1 olan ve teklife kapanma süresi geçen duyuru
        obj_id = "JgrLlrsr61OEADCLmyVWDWrVbg1"
        # Durumu 1 olan ve teklife kapanma süresi geçmeyen duyuru
        obj2_id = "2ZU7gZR2kfXa0OccQKtbQoueDdK"

        self.prepare_client('/bap_satin_alma_islemleri',
                            username='bap_koordinasyon_birimi_1')

        resp = self.client.post()
        # Satın alma duyurularının listelenme ekranı
        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
        # Düzenle butonuna basılır.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="duzenle",
                                object_id=obj2_id)
        # Duyuruya ait ad ve teklife kapanma tarihi değiştirilebilir.
        assert resp.json['forms']['schema']['title'] == "Duyuru Bilgileri Düzenle"
        # Değiştirilen bilgiler kaydedilir.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="kaydet",
                                form={'teklife_kapanma_tarihi': "10.07.2017"})

        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
        # Teklife kapat butonuna basılır.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="teklife_kapat",
                                object_id=obj_id)

        duyuru = BAPSatinAlma.objects.get(obj_id)
        # Teklife Kapatıldı durumuna geçildi mi kontrol edilir.
        assert duyuru.teklif_durum == 2
        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
        # Teklifleri Değerlendir butonuna basılır.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="degerlendir",
                                object_id=obj_id)

        assert "4 Kalem Kırtasiye Malzemesi Alımı" in resp.json['forms']['schema']['title']

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="isle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        assert "Test Firma 2" in resp.json['forms']['schema']['title']

        key_dict = {'7uvtCCHGqcjnAdhVMDtBKYiFQ2T': 0.5,
                    'BNfJoUkHVZKH2dmjzZEuJST4its': None,
                    'WD0K3k6syBXJOX9hkS5wBmnCQBD': 8,
                    'Jj8IRgcmS6HFNKPegm5wASOjUAB': None}

        list_node_data = []
        for key, birim in key_dict.items():
            kalem = BAPButcePlani.objects.get(key)
            data = {'adet': kalem.adet,
                    'birim_fiyat': birim,
                    'kalem': kalem.ad,
                    'key': key
                    }
            list_node_data.append(data)

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="kaydet",
                                form={'TeklifIsle': list_node_data})

        assert resp.json['msgbox']['title'] == "İşlem Mesajı"
        assert "Test Firma 2" in resp.json['msgbox']['msg']

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="degerlendir")

        assert resp.json['msgbox']['title'] == "Hata Mesajı"

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="duzenle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        time.sleep(2)
        for obj in resp.json['forms']['model']['TeklifIsle']:
            assert key_dict[obj['key']] == obj['birim_fiyat']

        for obj in list_node_data:
            if obj['key'] == 'WD0K3k6syBXJOX9hkS5wBmnCQBD':
                obj['birim_fiyat'] = 11.5
                key_dict['WD0K3k6syBXJOX9hkS5wBmnCQBD'] = obj['birim_fiyat']

        self.client.post(wf='bap_satin_alma_islemleri',
                         cmd="kaydet",
                         form={'TeklifIsle': list_node_data})

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="duzenle",
                                data_key="530g49RwA2nX5fzwEMWurrbqouN")

        for obj in resp.json['forms']['model']['TeklifIsle']:
            assert key_dict[obj['key']] == obj['birim_fiyat']

        self.client.post(wf='bap_satin_alma_islemleri',
                         cmd="geri_don")

        key_list = ['GqoC0MAcMAw2aedOcOi4JvjGFkd',
                    '1LqWUtM7s0Wsvj8rDYbvnGvYujy',
                    'GSX4LNZntJicEmD4k0DQ3u7M9ME']

        for key in key_list:
            self.client.post(wf='bap_satin_alma_islemleri',
                             cmd="isle",
                             data_key=key)

            self.client.post(wf='bap_satin_alma_islemleri',
                             cmd="kaydet",
                             form={'TeklifIsle': list_node_data})

        time.sleep(1)

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="degerlendir")

        assert resp.json['forms']['schema'][
                   'title'] == "4 Kalem Kırtasiye Malzemesi Alımı Satın Alma Duyurusuna Verilen Teklifler"

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="belirle")

        assert "4 Kalem Kırtasiye Malzemesi" in resp.json['forms']['schema']['title']

        key_dict = {'7uvtCCHGqcjnAdhVMDtBKYiFQ2T': 'QbuMU7XC8iG9oO18SqAUNlVjFXi',
                    'BNfJoUkHVZKH2dmjzZEuJST4its': None,
                    'WD0K3k6syBXJOX9hkS5wBmnCQBD': '2DsrZxp3dR6E6xZkDizahVYSMY6',
                    'Jj8IRgcmS6HFNKPegm5wASOjUAB': None}

        list_node_data = []
        for key, firma in key_dict.items():
            kalem = BAPButcePlani.objects.get(key)
            data = {'adet': kalem.adet,
                    'firma': firma,
                    'kalem': kalem.ad,
                    'key': key}
            list_node_data.append(data)

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="ilerle",
                                form={'KazananFirmalar': list_node_data})

        assert resp.json['forms']['schema']['title'] == "Kazanan Firmaların Onayı"

        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd="onayla")

        assert resp.json['msgbox']['title'] == "İşlem Bilgilendirme"

        satin_alma = BAPSatinAlma.objects.get(obj_id)
        BAPTeklifFiyatIsleme.objects.filter(satin_alma=satin_alma).delete()
        for teklif in BAPTeklif.objects.filter(satin_alma=satin_alma):
            teklif.fiyat_islemesi = False
            teklif.save()
        # Satın Alma Bilgilerini Güncelle butonuna basılır.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd='satin_alma',
                                object_id=obj_id)
        # Bütçe kalemi bilgilerinin listelenmesi ekranı
        assert resp.json['forms']['schema']['title'] == "Bütçe Kalemi Bilgilerinin Listesi"
        # Güncelle butonuna basılır.
        resp = self.client.post(wf='bap_satin_alma_islemleri',
                                cmd='guncelle')
        # Değiştirilen bilgiler kaydedilir ve duyuru listeleme ekranına dönüş yapılır.
        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
