# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from tests.fake.user import new_user
from ulakbus.models.personel import \
    Personel  # AdresBilgileri, KurumIciGorevlendirmeBilgileri, KurumDisiGorevlendirmeBilgileri
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
import random

__author__ = 'Halil İbrahim Yılmaz'


def yeni_personel():
    p = Personel()
    p.tckn = ints(length=11)
    p.ad = fake.first_name()
    p.soyad = fake.last_name()
    p.cinsiyet = gender()
    p.uyruk = fake.country()
    p.medeni_hali = marital_status(student=False)
    p.ikamet_adresi = fake.address()
    p.ikamet_il = fake.state()
    p.ikamet_ilce = fake.state()
    p.adres_2 = fake.address()
    p.adres_2_posta_kodu = fake.postcode()
    p.oda_no = fake.classroom_code()
    p.oda_tel_no = fake.phone_number()
    p.cep_telefonu = fake.phone_number()
    p.e_posta = fake.email()
    p.e_posta_2 = fake.email()
    p.e_posta_3 = fake.email()
    p.web_sitesi = "http://%s" % fake.domain_name()
    p.yayinlar = '\n'.join(fake.paragraphs())
    p.projeler = '\n'.join(fake.paragraphs())
    p.kan_grubu = blood_type()
    p.ehliyet = driver_license_class()
    p.verdigi_dersler = '\n'.join([fake.lecture() for _ in range(3)])
    p.unvan = random.choice(range(1, 5))
    p.biyografi = '\n'.join(fake.paragraphs(5))
    p.notlar = '\n'.join(fake.paragraphs(1))
    p.personel_turu = random.choice(['1', '2'])
    p.cuzdan_seri = id_card_serial()
    p.cuzdan_seri_no = ints(length=10)
    p.baba_adi = fake.first_name_male()
    p.ana_adi = fake.first_name_female()
    p.dogum_tarihi = birth_date(student=False)
    p.dogum_yeri = fake.state()

    username = fake.slug(u'%s-%s' % (p.ad, p.soyad))
    user = new_user(username=username)
    p.user = user

    p.save()
