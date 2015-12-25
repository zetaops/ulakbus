# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import Ogrenci, Donem, Program, Ders, Sube, Okutman, Sinav,\
    OgrenciProgram, OgrenciDersi, DersKatilimi, Borc, DegerlendirmeNot
from ulakbus.models.personel import Personel
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from user import new_user
import random
import datetime


def yeni_personel(personel_turu=1):
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
    p.personel_turu = personel_turu
    p.cuzdan_seri = id_card_serial()
    p.cuzdan_seri_no = ints(length=10)
    p.baba_adi = fake.first_name_male()
    p.ana_adi = fake.first_name_female()
    p.dogum_tarihi = birth_date(student=False)
    p.dogum_yeri = fake.state()
    p.medeni_hali = random.choice(['1', '2'])
    p.hizmet_sinifi = random.choice(range(1,30))

    username = fake.slug(u'%s-%s' % (p.ad, p.soyad))
    user = new_user(username=username)
    p.user = user

    p.save()
    return p


def yeni_okutman(personel):
    o = Okutman()
    o.ad = fake.first_name()
    o.soyad = fake.last_name()
    o.unvan = personel.unvan
    o.birim_no = personel.birim.yoksis_no
    o.personel = personel

    # duplicate data check
    try:
        o.save()
        return o
    except:
        return None


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
    o.e_posta = fake.email()
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
    d.ad = random.choice(["Güz", "Güz", "Bahar", "Bahar", "Yaz"])
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
    d.ad = fake.lecture()
    d.ders_dili = random.choice(["Turkce", "Turkce", "Turkce", "Ingilizce"])
    d.kod = ints(length=3)
    d.program = program
    d.donem = random.choice(Donem.objects.filter(guncel=True))
    d.personel = personel

    d.save()
    return d


def yeni_sube(ders, okutman):
    s = Sube()
    s.ad = fake.classroom_code()
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
    op.ogrenci_no = str(ints(11))
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
    dk.katilim_durumu = float(random.randint(50, 100))
    dk.ders = sube
    dk.ogrenci = ogrenci
    dk.okutman = okutman

    dk.save()
    return dk


def yeni_degerlendirme_notu(sinav, ogrenci):
    dn = DegerlendirmeNot()
    dn.puan = random.randint(0, 100)
    dn.yil = str(sinav.tarih.year)
    dn.donem = sinav.ders.donem.ad
    dn.ogretim_elemani = sinav.sube.okutman.ad
    dn.sinav = sinav
    dn.ogrenci = ogrenci
    dn.ders = sinav.ders

    dn.save()
    return dn


def yeni_borc(ogrenci, donem):
    b = Borc()
    b.miktar = random.randint(100, 999)
    b.para_birimi = random.choice([1, 1, 1, 2, 3])
    b.sebep = random.choice([1, 1, 1, 2, 3])
    b.son_odeme_tarihi = donem.baslangic_tarihi
    b.odeme_sekli = random.choice([1, 2])
    b.odeme_tarihi = donem.baslangic_tarihi - datetime.timedelta(random.randint(0, 30))
    b.odenen_miktar = b.miktar
    b.ogrenci = ogrenci
    b.donem = donem

    b.save()
    return b


def fake_data(personel_say=20, okutman_say=10, program_say=5, ders_say=5, sube_say=3, sinav_say=2, ogrenci_say=10):
    personel_list = [yeni_personel() for p in range(personel_say)]

    # okutman olmayan personellerden okutman olustur
    okutman_list = []
    for prs in random.sample(personel_list, okutman_say):
        okutman = yeni_okutman(prs)
        if okutman:
            okutman_list.append(okutman)

    # yoksis uzerindeki program birimleri
    yoksis_program_list = random.sample(Unit.objects.filter(unit_type='Program'), program_say)

    # yoksis program listesinden program olustur
    for yoksis_program in yoksis_program_list:
        program = yeni_program(yoksis_program)

        # programa ait dersler
        for dc in range(ders_say):
            personel = random.choice(personel_list)
            ders = yeni_ders(program, personel)

            # derse ait subeler
            for sc in range(sube_say):
                okutman = random.choice(okutman_list)
                sube = yeni_sube(ders, okutman)

                # subeye ait sinavlar
                sinav_liste = [yeni_sinav(sube) for snv in range(sinav_say)]

                # subeye ait ogrenciler
                ogrenci_liste = [yeni_ogrenci() for og in range(ogrenci_say)]
                for ogrenci in ogrenci_liste:
                    personel = random.choice(personel_list)

                    # ogrencinin program, ders, devamsizlik, borc bilgileri
                    ogrenci_program = yeni_ogrenci_program(ogrenci, program, personel)
                    yeni_ogrenci_dersi(sube, ogrenci_program)
                    yeni_ders_katilimi(sube, ogrenci, okutman)
                    yeni_borc(ogrenci, ders.donem)

                    # ogrenci not bilgisi
                    for sinav in sinav_liste:
                        yeni_degerlendirme_notu(sinav, ogrenci)
