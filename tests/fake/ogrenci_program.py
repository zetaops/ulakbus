# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import Ogrenci, Donem, Program, Ders, Sube, Okutman, Sinav, OgrenciProgram, OgrenciDersi, DersKatilimi
from ulakbus.models.personel import Personel
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from user import new_user
import random
import datetime


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
    # o.adres_2 = fake.address()
    # o.adres_2_posta_kodu = fake.postcode()
    # o.oda_no = fake.classroom_code()
    o.e_posta = fake.email()
    # o.web_sitesi = "http://%s" % fake.domain_name()
    # o.yayinlar = '\n'.join(fake.paragraphs())
    # o.projeler = '\n'.join(fake.paragraphs())
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
    return o


def yeni_donem():
    d = Donem()
    d.ad = fake.month_name()
    d.baslangic_tarihi = datetime.datetime(random.randint(2015, 2017),
                                           random.randint(1, 12),
                                           random.randint(1, 15))
    d.bitis_tarihi = d.baslangic_tarihi + datetime.timedelta(random.randint(30, 180))
    d.guncel = random.choice(True)

    d.save()
    return d


def yeni_program(yoksis_program):
    bolum = Unit.objects.filter(yoksis_no=yoksis_program.parent_unit_no)[0]

    p = Program()
    p.yoksis_no = yoksis_program.yoksis_no
    p.bolum_adi = bolum.name
    p.ucret = random.randint(100, 999)
    p.yil = str(random.randint(2014, 2016))
    p.adi = yoksis_program.name
    p.birim = yoksis_program
    p.bolum = bolum

    p.save()
    return p


def yeni_ders(program, personel):
    d = Ders()
    d.ad = "DERS_" + random.randint(1000, 9999)
    d.kod = ints(length=11)
    d.program = program
    d.donem = random.choice(Donem.objects.filter(guncel=True))
    d.personel = personel

    d.save()
    return d


def yeni_sube(ders, okutman):
    s = Sube()
    s.ad = "SUBE_" + random.randint(1000, 9999)
    s.kontenjan = random.randint(1, 500)
    s.dis_kontenjan = random.randint(1, 500)
    s.okutman = okutman
    s.ders = ders
    s.donem = ders.donem

    s.save()
    return s


def yeni_sinav(sube):
    s = Sinav()
    d = sube.donem
    s.tarih = d.baslangic_tarihi + \
              datetime.timedelta(
                      random.randint(1, (d.bitis_tarihi - d.baslangic_tarihi).days))
    s.yapilacagi_yer = sube.ad
    s.tur = random.randint(1, 7)
    s.sube = sube
    s.ders = sube.ders

    s.save()
    return s


def yeni_ogrenci_program(ogrenci, program, personel):
    op = OgrenciProgram()
    op.ogrenci_no = ints(11)
    op.giris_tarihi = datetime.datetime(int(program.yil), 10, 1)
    op.danisman = personel
    op.program = program
    op.ogrenci = ogrenci

    op.save()
    return op


def yeni_ogrenci_dersi(sube, ogrenci_program):
    od = OgrenciDersi()
    od.alis_bicimi = random.choice([1, 2])
    od.ders = sube
    od.ogrenci_program = ogrenci_program

    od.save()
    return od


def yeni_ders_katilimi(sube, ogrenci, okutman):
    dk = DersKatilimi()
    dk.katilim_durumu = random.uniform(1, 10)
    dk.ders = sube
    dk.ogrenci = ogrenci
    dk.okutman = okutman

    dk.save()
    return dk


def fake_data():
    personel_list = Personel.objects.filter(unvan=1)
    okutman_list = Okutman.objects.filter()
    yoksis_program_list = random.sample(Unit.objects.filter(unit_type='Program'), random.randint(3,10))

    for yoksis_program in yoksis_program_list:
        program = yeni_program(yoksis_program)

        ders_count = random.randint(3,10)
        for dc in range(ders_count):
            personel = random.choice[personel_list]
            ders = yeni_ders(program, personel)

            sube_count = random.randint(1,3)
            for sc in range(sube_count):
                okutman = random.choice[okutman_list]
                sube = yeni_sube(ders, okutman)

                ogrenci_liste = [yeni_ogrenci().user.username for og in range(random.randint(3,10))]
                for ogrenci in ogrenci_liste:
                    personel = random.choice[personel_list]

                    ogrenci_program = yeni_ogrenci_program(ogrenci, program, personel)
                    ogrenci_dersi = yeni_ogrenci_dersi(sube, ogrenci_program)
                    ders_katilimi = yeni_ders_katilimi(sube, ogrenci, okutman)

                sinav_count = random.randint(2,3)
                for scnt in range(sinav_count):
                    sinav = yeni_sinav(sube)


