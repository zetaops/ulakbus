# -*-  coding: utf-8 -*-
"""Öğrenci Mezuniyet kaydı iş akışına ait class ve test methodlarını barındırır.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'H.İbrahim Yılmaz (drlinux)'

import time
import os
from pyoko.manage import FlushDB, LoadData
from ulakbus.models import Ogrenci, OgrenciProgram, User
from .base_test_case import BaseTestCase

class TestCase(BaseTestCase):
    """Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_setup(self):
        """Öğrenci mezuniyet iş akışı test edilmeden önce veritabanı boşaltılır,
        belirtilen dosyadaki veriler veritabanına yüklenir.

        """

        import sys
        if '-k-nosetup' in sys.argv:
            return

        # Bütün kayıtlar db'den silinir.
        FlushDB(model='all').run()
        # Belirtilen dosyadaki kayıtları ekler.
        LoadData(path=os.path.join(os.path.expanduser('~'),
                                   'ulakbus/tests/fixtures/ogrenci_mezuniyet.csv')).run()
        time.sleep(1)


    def test_ogrenci_mezuniyet(self):
        """test_user kullanıcısı giriş yapar ve RnKyAoVDT9Hc89KEZecz0kSRXRF keyine sahip öğrencinin
        kayıtlı olduğu UEGET7qn9CDj9VEj4n0nbQ7m89d keyine sahip TÜRK DİLİ VE EDEBİYATI ÖĞRETMENLİĞİ
        programından mezuniyet kaydını yapar.

        Bu iş akışı iki adımadan oluşmaktadır:

        İlk adımda öğrencinin kayıtlı olduğu bölümler listelenir.

        İkinci adımda ise seçilen bölüm üzerinden mezuniyet kaydı yapılır ve ekrana yapılan işlemle
        ilgi özet bilgi basılır. Mezuniyet tarihi olarak, öğrencinin en son girdiği sınav tarihi
        eklenir.

        Öğrencinin en son girdiği sınavın tarihi ile ``OgrenciProgram`` modelinden dönen mezuniyet
        tarihinin aynı olması beklenir.

        """

        #ogrenci_mezuniyet/OgrenciProgram/do/form?ogrenci_id=RnKyAoVDT9Hc89KEZecz0kSRXRF