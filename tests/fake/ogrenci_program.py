# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import Ogrenci, Donem, Program, Ders, Sube, Okutman, Sinav, \
    OgrenciProgram, OgrenciDersi, DersKatilimi, Borc, DegerlendirmeNot, HariciOkutman
from ulakbus.models.personel import Personel
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from user import new_user
import random
import datetime


def yeni_personel(personel_turu=1, personel_say=1):
    """
    Rastgele verileri ve parametre olarak verilen veriyi kullanarak
    yeni personel kaydı oluştururup kaydeder. Oluşturulan kayıtları liste olarak döndürür.

    Args:
        personel_turu (Personel): Personel türü
        personel_say : Oluşturulacak personel sayısı

    Returns:
        Personel: Yeni personel listesi

    """

    personel_list = []

    for i in range(personel_say):
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
        p.hizmet_sinifi = random.choice(range(1, 30))

        username = fake.slug(u'%s-%s' % (p.ad, p.soyad))
        user = new_user(username=username)
        p.user = user

        p.save()
        personel_list.append(p)
    return personel_list


def yeni_okutman(personel):
    """
    Rastgele verileri ve parametre olarak verilen veriyi kullanarak
    yeni okutman kaydı oluştururup kaydeder.

    Args:
        personel (Personel): Personel nesnesi

    Returns:
        Okutman: Yeni okutman kaydı

    """

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

def yeni_harici_okutman(harici_okutman_say=1):
    """
    Rastgele verileri kullanarak yeni harici okutman kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        harici_okutman_say : Oluşturulacak harici okutman sayısı

    Returns:
        HariciOkutman: Yeni harici okutman listesi

    """

    harici_okutman_list = []

    for i in range(harici_okutman_say):
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
        ho.telefon_no = fake.phone_number()
        ho.e_posta = fake.email()
        ho.e_posta_2 = fake.email()
        ho.e_posta_3 = fake.email()
        ho.web_sitesi = "http://%s" % fake.domain_name()
        ho.yayinlar = '\n'.join(fake.paragraphs())
        ho.projeler = '\n'.join(fake.paragraphs())
        ho.kan_grubu = blood_type()
        ho.ehliyet = driver_license_class()
        ho.verdigi_dersler = '\n'.join([fake.lecture() for _ in range(3)])
        ho.unvan = random.randint(1, 5)
        ho.biyografi = '\n'.join(fake.paragraphs(5))
        ho.notlar = '\n'.join(fake.paragraphs(1))
        ho.cuzdan_seri = id_card_serial()
        ho.cuzdan_seri_no = ints(length=10)
        ho.baba_adi = fake.first_name_male()
        ho.ana_adi = fake.first_name_female()
        ho.dogum_tarihi = birth_date(student=False)
        ho.dogum_yeri = fake.state()
        ho.save()
        harici_okutman_list.append(ho)
    return harici_okutman_list

def yeni_ogrenci(ogrenci_say=1):
    """
    Rastgele veriler kullanarak yeni öğrenci kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        ogrenci_say : Oluşturulacak ogrenci sayısı

    Returns:
        Ogrenci: Yeni öğrenci kaydı

    """
    ogrenci_list = []
    for i in range(ogrenci_say):
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
        ogrenci_list.append(o)
    return ogrenci_list


def yeni_donem(donem_say=1):
    """
    Rastgele veriler kullanarak yeni dönem kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        donem_say : Oluşturulacak donem sayısı

    Returns:
        Donem: Yeni dönem listesi

    """
    donem_list = []

    for i in range(donem_say):
        d = Donem()
        d.ad = random.choice(["Güz", "Güz", "Bahar", "Bahar", "Yaz"])
        d.baslangic_tarihi = datetime.datetime(random.randint(2015, 2017),
                                               random.randint(1, 12),
                                               random.randint(1, 15))
        d.bitis_tarihi = d.baslangic_tarihi + datetime.timedelta(random.randint(30, 180))
        d.guncel = random.choice(True)

        d.save()
        donem_list.append(d)
    return donem_list


def yeni_program(yoksis_program, program_say=1):
    """
    Rastgele verileri ve parametre olarak verilen veriyi
    kullanarak yeni program kaydı oluşturur ve kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        yoksis_program (Unit): Yöksis programı
        program_say : Oluşturulacak program sayısı

    Returns:
        Program: Yeni program listesi

    """

    bolum = Unit.objects.filter(yoksis_no=yoksis_program.parent_unit_no)[0]
    program_list=[]

    for i in range(program_say):
        p = Program()
        p.yoksis_no = yoksis_program.yoksis_no
        p.bolum_adi = bolum.name
        p.ucret = random.randint(100, 999)
        p.yil = str(random.randint(2014, 2016))
        p.adi = yoksis_program.name
        p.birim = yoksis_program
        p.bolum = bolum

        p.save()
        program_list.append(p)
    return program_list


def yeni_ders(program, personel, ders_say=1):
    """
    Rastgele verileri ve parametre olarak verilen veriyi
    kullanarak yeni ders kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        program (Program): Program nesnesi
        personel (Personel): Personel nesnesi
        ders_say : Oluşturulacak Ders sayısı

    Returns:
        Ders: Yeni ders listesi

    """

    ders_list = []
    for i in range(ders_say):
        d = Ders()
        d.ad = fake.lecture()
        d.ders_dili = random.choice(["Turkce", "Turkce", "Turkce", "Ingilizce"])
        d.kod = ints(length=3)
        d.program = program
        d.donem = random.choice(Donem.objects.filter(guncel=True))
        d.ders_koordinatoru = personel

        d.save()
        ders_list.append(d)
    return ders_list


def yeni_sube(ders, okutman, sube_say=1):
    """
    Rastgele verileri ve parametre olarak verilen veriyi
    kullanarak yeni şube kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        ders (Ders): Ders nesnesi
        okutman (Okutman): Okutman nesnesi
        sube_say : Oluşturulacak sube sayısı

    Returns:
        Sube: Yeni şube listesi

    """

    sube_list = []
    for i in range(sube_say):
        s = Sube()
        s.ad = fake.classroom_code()
        s.kontenjan = random.randint(1, 500)
        s.dis_kontenjan = random.randint(1, 500)
        s.okutman = okutman
        s.ders = ders
        s.donem = ders.donem
        s.save()
        sube_list.append(s)
    return sube_list


def yeni_sinav(sube, sinav_say=1):
    """
    Rastgele verileri ve parametre olarak verilen veriyi
    kullanarak yeni sınav kaydı oluştururup kaydeder.
    Oluşturulan kayıtları liste olarak döndürür.

    Args:
        sube (Sube): Şube nesnesi
        sinav_say : Oluşturulacak sınav sayısı

    Returns:
        Sinav: Sinav nesne listesi

    """

    sinav_list = []
    for i in range(sinav_say):
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
        sinav_list.append(s)
    return sinav_list

def yeni_ogrenci_program(ogrenci, program, personel):
    """
    Rastgele verileri ve parametre olarak verilen verileri
    kullanarak yeni öğrenci programı kaydı oluştururup kaydeder.

    Args:
        ogrenci (Ogrenci): Öğrenci nesnesi
        personel (Personel): Personel nesnesi
        program (Program): Program nesnesi

    Returns:
        OgrenciProgram: Yeni öğrenci program kaydı

    """

    op = OgrenciProgram()
    op.ogrenci_no = str(ints(11))
    op.giris_tarihi = datetime.datetime(int(program.yil), 10, 1)
    op.danisman = personel
    op.program = program
    op.ogrenci = ogrenci

    op.save()
    return op


def yeni_ogrenci_dersi(sube, ogrenci_program):
    """
    Rastgele verileri ve parametre olarak verilen verileri
    kullanarak öğrenci ders kaydı oluştururup kaydeder.

    Args:
        sube (Sube): Şube nesnesi
        ogrenci_program (OgrenciProgram): Öğrenci Programı nesnesi

    Returns:
        OgrenciDersi: Yeni öğrenci ders kaydı

    """

    od = OgrenciDersi()
    od.alis_bicimi = random.choice([1, 2])
    od.ders = sube
    od.ogrenci_program = ogrenci_program

    od.save()
    return od


def yeni_ders_katilimi(sube, ogrenci, okutman):
    """
    Rastgele verileri ve parametre olarak verilen verileri
    kullanarak yeni ders katılım kaydı oluştururup kaydeder.

    Args:
        sube (Sube): Şube
        ogrenci (Ogrenci): Öğrenci nesnesi
        okutman (Okutman): Okutman nesnesi

    Returns:
        DersKatilimi: Yeni ders katılım kaydı

    """

    dk = DersKatilimi()
    dk.katilim_durumu = float(random.randint(50, 100))
    dk.ders = sube
    dk.ogrenci = ogrenci
    dk.okutman = okutman

    dk.save()
    return dk


def yeni_degerlendirme_notu(sinav, ogrenci):
    """
    Rastgele verileri ve parametre olarak verilen verileri
    kullanarak yeni değerlendirme notu kaydı oluşturup kaydeder.

    Args:
        sinav (Sinav): Sınav nesnesi
        ogrenci (Ogrenci): Öğrenci nesnesi

    Returns:
        DegerlendirmeNot: Yeni değerlendirme notu kaydı

    """

    try:
        sinav_program = sinav.ders.program
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci=ogrenci,program=sinav_program)[0]
        dn = DegerlendirmeNot()
        dn.puan = random.randint(0, 100)
        dn.yil = str(sinav.tarih.year)
        dn.donem = sinav.ders.donem.ad
        dn.ogretim_elemani = sinav.sube.okutman.ad
        dn.sinav = sinav
        dn.ogrenci_no = ogrenci_program.ogrenci_no
        dn.ogrenci = ogrenci
        dn.ders = sinav.ders
        dn.save()
        return dn
    except:
        print("Ogrenci Programi Bulunamadi")


def yeni_borc(ogrenci, donem):
    """
    Rastgele verileri ve parametre olarak verilen verileri
    kullanarak yeni borç kaydı oluştururup kaydeder.

    Args:
        ogrenci (Ogrenci): Öğrenci nesnesi
        donem (Donem): Dönem nesnesi

    Returns:
        Borc: Yeni borç kaydı

    """

    b = Borc()
    b.miktar = float(random.randint(100, 999))
    b.para_birimi = random.choice([1, 1, 1, 2, 3])
    b.sebep = random.choice([1, 1, 1, 2, 3])
    b.son_odeme_tarihi = donem.baslangic_tarihi
    b.tahakkuk_referans_no = str(ints(11))
    b.aciklama = '\n'.join(fake.paragraphs(1))
    b.ogrenci = ogrenci
    b.donem = donem

    b.save()
    return b


def fake_data(personel_say=20, okutman_say=10, program_say=5, ders_say=5, sube_say=3, sinav_say=2, ogrenci_say=10):
    """
    Rastgele verileri ve parametre olarak verilen verileri kullanarak
    yeni okutman, program, ders, şube, sınav, borc ve ders katılımı kayıtları
    oluştururup kaydeder.

    Args:
        personel_say (int): Personel sayısı
        okutman_say (int): Okutman sayısı
        program_say (int): Program sayısı
        ders_say (int): Ders sayısı
        sube_say (int): Şube sayısı
        sinav_say (int): Sınav sayısı
        ogrenci_say (int): Öğrenci sayısı

    """

    personel_list = [yeni_personel() for p in range(personel_say)]

    # okutman olmayan personellerden okutman olustur.
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
