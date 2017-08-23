# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import BAPButcePlani
from ulakbus import settings


class TestCase(BaseTestCase):
    """
    Duyuruda olan satın alma duyurularının listelenmesini ve listelenen duyurulara ait detay bilgilerinin görüntülenmesi işlemlerini içerir.

    """

    def test_bap_satin_alma_islemleri(self):
        object_id = "2ZU7gZR2kfXa0OccQKtbQoueDdK"
        self.prepare_client('/bap_satin_alma_duyurulari_listeleme',
                            username='bap_koordinasyon_birimi_1')

        resp = self.client.post()
        # Duyuruda olan satın alma duyurularının listelenme ekranı
        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
        # Duyuruya ait detay butonuna tıklanır.
        resp = self.client.post(cmd="detay", object_id=object_id)
        # Bütçe Kalemleri Listeleme Ekranı
        assert resp.json['forms']['schema'][
                   'title'] == "4 Kalem Malzeme Alımı Satın Alma Duyurusu Bütçe Kalemleri"
        # Şartname dosyasını indirmek için indir butonuna tıklanır.
        resp = self.client.post(cmd="indir", data_key='8W16zg1iEvrrbQXRpM4JFw3oR62')

        butce_plani = BAPButcePlani.objects.get('8W16zg1iEvrrbQXRpM4JFw3oR62')
        # Şartname dosyası indirildi mi kontrol edilir.
        assert resp.json['download_url'] == "%s%s" % (
        settings.S3_PUBLIC_URL, butce_plani.teknik_sartname.sartname_dosyasi)

        self.client.post()
        # Geri dön butonuna tıklanır ve listeleme ekranına dönülür.
        resp = self.client.post(cmd='geri_don')
        # Duyuruda olan satın alma duyurularının listelenme ekranı
        assert resp.json['forms']['schema']['title'] == "Satın Alma Duyurularının Listesi"
