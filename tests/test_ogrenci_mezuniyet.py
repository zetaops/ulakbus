# -*-  coding: utf-8 -*-
"""Öğrenci Mezuniyet kaydı iş akışına ait class ve test methodlarını barındırır.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time
from ulakbus.models import Ogrenci, OgrenciProgram, User, Program, DegerlendirmeNot
from zengine.lib.test_utils import BaseTestCase

__author__ = 'H.İbrahim Yılmaz (drlinux)'


class TestCase(BaseTestCase):
    """Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ogrenci_mezuniyet(self):
        """ogrenci_isleri_1 kullanıcısı giriş yapar ve
        RnKyAoVDT9Hc89KEZecz0kSRXRF keyine sahip öğrencinin
        kayıtlı olduğu UEGET7qn9CDj9VEj4n0nbQ7m89d keyine sahip
        proggramdan mezuniyet kaydını yapar.

        Bu iş akışı iki adımadan oluşmaktadır:

        İlk adımda öğrencinin kayıtlı olduğu bölümler listelenir.

        İkinci adımda ise seçilen bölüm üzerinden mezuniyet kaydı
        yapılır ve ekrana yapılan işlemle ilgi özet bilgi basılır.
        Mezuniyet tarihi olarak, öğrencinin en son girdiği sınav
        tarihi eklenir.

        Öğrencinin en son girdiği sınavın tarihi ile `OgrenciProgram`
        modelinden dönen mezuniyet tarihinin aynı olması beklenir.

        ogrenci_isleri_1 adlı kullanıcıya çıkış yaptırılır.

        """

        ogrenci_id = "RnKyAoVDT9Hc89KEZecz0kSRXRF"
        ogrenci_program_id = "UEGET7qn9CDj9VEj4n0nbQ7m89d"
        program_id = "7GPhFaFbPqysh7mnkkd9Bq3cmCh"

        # veritabanından personel_isleri_1 seçilir
        usr = User.objects.get(username='ogrenci_isleri_1')
        ogrenci = Ogrenci.objects.get(ogrenci_id)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        time.sleep(1)

        self.prepare_client('/ogrenci_mezuniyet', user=usr)

        self.client.post(id=ogrenci_id, model="OgrenciProgram", param="ogrenci_id",
                         wf="ogrenci_mezuniyet")

        program = {'program': ogrenci_program_id, 'sec': 1}
        self.client.post(model="OgrenciProgram", wf="ogrenci_mezuniyet", form=program)

        time.sleep(3)

        ogrenci_sinav_list = DegerlendirmeNot.objects.set_params(
            rows=1, sort='sinav_tarihi desc').filter(ogrenci=ogrenci_program.ogrenci)
        son_sinav_tarihi = ogrenci_sinav_list[0].sinav_tarihi
        program_secim = Program.objects.get(program_id)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci, program=program_secim)

        assert son_sinav_tarihi == ogrenci_program.mezuniyet_tarihi
