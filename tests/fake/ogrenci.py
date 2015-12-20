# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models.ogrenci import Ogrenci
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from user import new_user
import random

__author__ = 'Halil İbrahim Yılmaz'


def yeni_ogrenci():
    o = Ogrenci()
    o.tckn = ints(length=11)
    o.ad = fake.first_name()
    o.soyad = fake.last_name()
    o.cinsiyet = gender()
    o.uyruk = fake.country()
    o.medeni_hali = marital_status(student=True)
    o.ikamet_adresi = fake.address()
    o.ikamet_il = fake.state()
    o.ikamet_ilce = fake.state()
    o.adres_2 = fake.address()
    o.adres_2_posta_kodu = fake.postcode()
    o.oda_no = fake.classroom_code()
    o.e_posta = fake.email()
    o.web_sitesi = "http://%s" % fake.domain_name()
    o.yayinlar = '\n'.join(fake.paragraphs())
    o.projeler = '\n'.join(fake.paragraphs())
    o.kan_grubu = blood_type()
    o.ehliyet = driver_license_class()
    o.cuzdan_seri = id_card_serial()
    o.cuzdan_seri_no = ints(length=10)
    o.baba_adi = fake.first_name_male()
    o.ana_adi = fake.first_name_female()
    o.dogum_tarihi = birth_date(student=True)
    o.dogum_yeri = fake.state()
    o.tel_no = fake.phone_number()

    username = fake.slug(u'%s-%s' % (o.ad, o.soyad))
    user = new_user(username=username)
    o.user = user

    o.save()
