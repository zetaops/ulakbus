# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.manage import FlushDB, LoadData
from zengine.lib.test_utils import *
import os
import time


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_setup(self):
        """
        Okutman not girişi iş akışı test edilmeden önce aşağıda
        tanımlı ön hazırlıklar yapılır.

        """

        # Bütün kayıtlar db'den silinir.
        FlushDB(model='all').run()
        # Belirtilen dosyadaki kayıtları ekler.
        LoadData(path=os.path.join(os.path.expanduser('~'), 'ulakbus/tests/fixtures/okutman_not_girisi.csv')).run()

    def test_okutman_not_girisi(self):
        """
        Okutman not girişi iş akışını test eder.

        """
        
        # Ders şubesi seçilir.
        self.client.post(cmd='Ders Şubesi Seçin',
                         form=dict(sube='S7z8bvdNCBFSd9iCvQrb7O1pQ75', sec=1))
        # Seçilen şubeye ait sınav seçilir.
        self.client.post(cmd='Sınav Seçin',
                         form=dict(sinav='7isfBEsi96AVDZdp2o33mQoWemJ', sec=1))
        # Ders seçim ekranına geri döner
        self.client.post(cmd='ders_sec',
                         form=dict(sinav_secim='null', ders_secim=1),
                         flow='ders_secim_adimina_don')
        # Ders şubesi seçilir.
        self.client.post(cmd='Ders Şubesi Seçin',
                         form=dict(sube='PRGgozMfVXSrAqyO2aMnjS6aBQo', sec=1))
        # Sınav seçilir.
        resp = self.client.post(cmd='Sınav Seçin',
                                form=dict(sinav='IvXH1cqyYoHznv0iRV4FjLvXWwz', sec=1))

        # Dersler okutman tarafından onaylanmamışsa;
        assert 'inline_edit' in resp.json['forms']

        # Kayıtlar önizlenir.
        self.client.post(cmd='not_kontrol',
                         form=dict(Ogrenciler=resp.json['forms']['model']['Ogrenciler'], kaydet=1))

        # Sınav notları onaylanıp kaydedilir.
        # İş akışı bu adımdan sonra sona erer.
        resp = self.client.post(cmd='not_kaydet',
                                flow='end',
                                form=dict(kaydet_ve_sinav_sec='null', kaydet=1, kaydet_ve_ders_sec='null',
                                          not_duzenle='null', not_onay='null'))
        assert 'msgbox' in resp.json
