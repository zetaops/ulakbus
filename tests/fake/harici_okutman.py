# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import HariciOkutman
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from random import random, randint

__author__ = 'Halil İbrahim Yılmaz'


def yeni_harici_okutman():
    ho = HariciOkutman()
    ho.tckn = ints(length=11)
    ho.ad = fake.first_name()
    ho.soyad = fake.last_name()
    ho.cinsiyet = gender()
    ho.uyruk = fake.country()
    ho.medeni_hali = marital_status(student=False)
    ho.ikamet_adresi = fake.address()
    ho.ikamet_il = fake.state()
    ho.ikamet_ilce = fake.state()
    ho.adres_2 = fake.address()
    ho.adres_2_posta_kodu = fake.postcode()
    ho.oda_no = fake.classroom_code()
    ho.oda_tel_no = fake.phone_number()
    ho.cep_telefonu = fake.phone_number()
    ho.e_posta = fake.email()
    ho.e_posta_2 = fake.email()
    ho.e_posta_3 = fake.email()
    ho.web_sitesi = "http://%s" % fake.domain_name()
    ho.yayinlar = '\n'.join(fake.paragraphs())
    ho.projeler = '\n'.join(fake.paragraphs())
    ho.kan_grubu = blood_type()
    ho.ehliyet = driver_license_class()
    ho.verdigi_dersler = '\n'.join([fake.lecture() for _ in range(3)])
    ho.unvan = randint(1, 5)
    ho.biyografi = '\n'.join(fake.paragraphs(5))
    ho.notlar = '\n'.join(fake.paragraphs(1))
    ho.cuzdan_seri = id_card_serial()
    ho.cuzdan_seri_no = ints(length=10)
    ho.baba_adi = fake.first_name_male()
    ho.ana_adi = fake.first_name_female()
    ho.dogum_tarihi = birth_date(student=False)
    ho.dogum_yeri = fake.state()
    ho.save()