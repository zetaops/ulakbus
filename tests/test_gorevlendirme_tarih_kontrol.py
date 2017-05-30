# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import datetime
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import KurumDisiGorevlendirmeBilgileri
from ulakbus.models import KurumIciGorevlendirmeBilgileri
from ulakbus.models import Personel
from zengine.lib.test_utils import BaseTestCase
import pytest



class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_gorevlendirme_tarih_kontrol(self):
        """

        """
        personel = Personel()
        personel.save()

        # gorevlendirme zamanlari (gorev_baslama(ay-gun),gorev_bitis(ay-gun)) olarak belirtilmiştir.
        # default yil 2017.
        gorevlendirme_zamanlari = [((1, 3), (1, 10)), ((1, 12), (1, 15)), ((3, 15), (3, 20)), ((7, 16), (8, 16))]

        # gorevlendirme_zamanlari'ndaki tarihlerle uyusmayacak sekilde tarihler yine belirtilen formatta seçilmiştir.
        invalid_gorevlendirme_zamanlari = [((1, 2), (1, 5)), ((1, 11), (1, 20)), ((1, 11), (4, 1)), ((7, 20), (8, 10)),
                                           ((8, 15), (8, 20)), ((1, 10), (1, 12)), ((2, 20), (2, 2)), ((1, 15), (1, 15))]
        # gorevlendirme_zamanlari ile uyusan sekilde belirtilen formatta tarihler secilmistir.
        valid_gorevlendirme_zamanlari = [((1, 1), (1, 2)), ((11, 6), (11, 6)), ((2, 2), (2, 20)), ((9, 9), (9, 11))]

        for counter, tarih in enumerate(gorevlendirme_zamanlari):
            if counter % 2 == 0:
                gorevlendirme = KurumIciGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )
            else:
                gorevlendirme = KurumDisiGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )
            gorevlendirme.blocking_save()

        mevcut_gorev_sayisi = KurumDisiGorevlendirmeBilgileri.objects.filter(personel=personel).count() + \
                              KurumIciGorevlendirmeBilgileri.objects.filter(personel=personel).count()

        for counter, tarih in enumerate(invalid_gorevlendirme_zamanlari):
            if counter % 2 == 0:
                invalid_gorevlendirme = KurumIciGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )
            else:
                invalid_gorevlendirme = KurumDisiGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )
            with pytest.raises(Exception):
                invalid_gorevlendirme.blocking_save()
            assert invalid_gorevlendirme.key is None

        for counter, tarih in enumerate(valid_gorevlendirme_zamanlari):
            if counter % 2 == 0:
                valid_gorevlendirme = KurumIciGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )

            else:
                valid_gorevlendirme = KurumDisiGorevlendirmeBilgileri(
                    personel=personel,
                    baslama_tarihi=datetime.date(2017, tarih[0][0], tarih[0][1]),
                    bitis_tarihi=datetime.date(2017, tarih[1][0], tarih[1][1])
                )

            assert valid_gorevlendirme.blocking_save()

            valid_gorevlendirme.baslama_tarihi = datetime.date(2017, 1, 13)
            valid_gorevlendirme.bitis_tarihi = datetime.date(2017, 2, 13)

            with pytest.raises(Exception):
                valid_gorevlendirme.blocking_save()

        guncel_gorev_sayisi = KurumDisiGorevlendirmeBilgileri.objects.filter(personel=personel).count() + \
                              KurumIciGorevlendirmeBilgileri.objects.filter(personel=personel).count()
        assert guncel_gorev_sayisi == mevcut_gorev_sayisi + len(valid_gorevlendirme_zamanlari)

        personel.blocking_delete()
        KurumIciGorevlendirmeBilgileri.objects.filter(personel=personel).delete()
        KurumDisiGorevlendirmeBilgileri.objects.filter(personel=personel).delete()


