# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import datetime

from ulakbus.models import BAPDuyurular
from ulakbus import settings

from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    def test_duyuru_goruntule(self):
        eklenme_tarihi = datetime.strptime('06.06.2017', '%d.%m.%Y').date()
        son_gecerlilik_tarihi = datetime.strptime('30.06.2017', '%d.%m.%Y').date()

        duyuru = BAPDuyurular()
        duyuru.duyuru_baslik = 'Test Duyuru Başlıgı'
        duyuru.duyuru_icerik = 'Duyurunun yapılacağı içerik kısmı'
        duyuru.eklenme_tarihi = eklenme_tarihi
        duyuru.son_gecerlilik_tarihi = son_gecerlilik_tarihi
        duyuru.yayinlanmis_mi = True
        duyuru.EkDosyalar(ek_dosya='TestDosyasi.txt',
                          dosya_aciklamasi='Dosya ile ilgili aciklama')
        duyuru.save()

        yayinlanan_duyuru_sayisi = BAPDuyurular.objects.all(yayinlanmis_mi=True).count()

        self.prepare_client('/bap_duyurulari_goruntule', username='ulakbus')
        resp = self.client.post()
        assert yayinlanan_duyuru_sayisi == len(resp.json['objects']) - 1
        assert resp.json['object_title'] == 'BAP Genel Duyurular'

        resp = self.client.post(cmd='detay', object_id=duyuru.key)

        assert resp.json['object']['Başlık'] == duyuru.duyuru_baslik
        assert resp.json['object']['Duyuru'] == duyuru.duyuru_icerik

        resp = self.client.post(cmd='belge_indir', form={'indir': 1})

        assert resp.json['download_url'] == "%s%s-duyuru-belgeler.zip" % (
                    settings.S3_PUBLIC_URL, duyuru.__unicode__().replace(' ', ''))
