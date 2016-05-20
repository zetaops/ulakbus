# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.auth import Unit
from ulakbus.models.ogrenci import Ogrenci, Donem, Program, Ders, Sube, Okutman, Sinav
from ulakbus.models.ogrenci import OgrenciProgram, OgrenciDersi, DersKatilimi
from ulakbus.models.ogrenci import Borc, DegerlendirmeNot, HariciOkutman, DonemDanisman
from ulakbus.models.personel import Personel
from ulakbus.models.buildings_rooms import Campus, Building, Room, RoomType
from .general import ints, gender, marital_status, blood_type, create_fake_geo_data
from .general import driver_license_class, id_card_serial, birth_date
from .general import fake
from user import new_user
import random
import datetime

__author__ = 'Halil İbrahim Yılmaz'


class FakeDataGenerator:
    def __init__(self):
        pass

    @staticmethod
    def yeni_kampus(kampus_say=2):
        """
        Rastegele verilerle kampus listesi oluşturur.

        Args:
            kampus_say (int): oluşturulacak kampüs sayısı

        Return:
            campus_list (list): kampus listesi

        """

        kampus_list = [
            "Kuzey Kampüsü",
            "Güney Kampüsü",
            "Doğu Kampüsü",
            "Batı Kampüsü",
        ]

        campus_list = []

        for i in range(kampus_say):
            c = Campus(code=ints(length=5), name="%s - %s" % (random.choice(kampus_list), ints(3)))
            c.coordinate_x, c.coordinate_y = create_fake_geo_data()
            c.save()
            campus_list.append(c)

        return campus_list

    @staticmethod
    def yeni_donem(donem_say=1, guncel=False):
        """
        Rastegele verilerle kampus listesi oluşturur.

        Args:
            donem_say (int): oluşturulacak donem sayısı
            guncel (bool): guncel donem bilgisi

        Return:
            donem_list (list): donem listesi

        """

        donemler = [
            ("Güz", 9, 2),
            ("Bahar", 2, 7),
            ("Yaz", 7, 9),
        ]
        donem_list = []

        for i in range(donem_say):
            ad, baslangic, bitis = random.choice(donemler)
            d = datetime.datetime.now()
            year = d.year
            baslangic_tarihi = datetime.datetime(d.year, baslangic, 1)
            if ad == "Güz":
                year += 1
            bitis_tarihi = datetime.datetime(year, bitis, 1)

            donem = Donem(ad="%s - %s" % (ad, year), baslangic_tarihi=baslangic_tarihi,
                          bitis_tarihi=bitis_tarihi)

            if Donem.objects.filter(ad="%s - %s" % (ad, year)).count() < 1:
                if guncel:
                    for d in Donem.objects.filter():
                        d.guncel = False
                        d.save()
                    donem.guncel = True
                donem.save()
                donem_list.append(donem)

            if Donem.objects.filter(guncel=True).count() < 1:
                donem.guncel = True
                donem.save()

        return donem_list

    def yeni_bina(self):
        """
        Her bir fakulte icin, fakulte adi ile bir bina kaydı oluşturup kaydeder.
        Olusturulan her bir bina icin rastgele oda kayitlari olusturur.

        Returns:
            building_list (list): bina listesi
            room_list (list): oda listesi

        """
        import time

        building_list = []
        room_list = []
        uni = Unit.objects.filter(parent_unit_no=0)[0]
        campus = random.choice(Campus.objects.filter())

        # Eğer daha önceden oluşturulmuş oda tipi yoksa
        if RoomType.objects.count() < 1:
            self.yeni_oda_tipi()
            time.sleep(3)

        faculty_list = Unit.objects.filter(parent_unit_no=uni.yoksis_no)

        for faculty in faculty_list:
            b = Building()
            b.code = faculty.yoksis_no
            b.name = faculty.name
            b.coordinate_x = campus.coordinate_x
            b.coordinate_y = campus.coordinate_y
            b.campus = campus
            b.save()
            building_list.append(b.name)
            time.sleep(1)
            new_room = self.yeni_derslik(building=b, parent_unit_no=faculty.yoksis_no,
                                         count=random.choice(range(10, 20)))
            room_list.append(new_room)

        return building_list, room_list

    @staticmethod
    def yeni_derslik(building, parent_unit_no, count=1):
        """
        Rastgele verileri ve parametre olarak verilen verileri kullanarak
        yeni derslik kaydı oluştururup kaydeder.

        Args:
            building (Building): Bina
            parent_unit_no (int): Birim no
            count (int): Oluşturulacak dersliğin sayısı

        Return:
            room_list (list): Sinif listesi

        """

        room_list = []
        unit_list = Unit.objects.filter(parent_unit_no=parent_unit_no, unit_type="Bölüm")
        room_types = RoomType.objects.filter()
        for i in range(1, count):
            room = Room(
                code=fake.classroom_code(),
                name=fake.classroom(),
                building=building,
                room_type=random.choice(room_types),
                floor=ints(2),
                capacity=random.choice(range(30, 100)),
                is_active=True
            )
            for unit in unit_list:
                room.RoomDepartments(unit=unit)
            room.save()
            room_list.append("%s - %s" % (room.code, room.name))
        return room_list

    @staticmethod
    def yeni_oda_tipi(oda_tip="Derslik"):
        """
        RoomType modeli için verilen tipte oda tipi oluşturur. Varsayılan tip Derslik'tir

        Args:
            oda_tip (str) : Oluşturulacak oda tipinin adı

        Returns:
             room_type (RoomType) : RoomType nesnesi

        """

        room_type = RoomType(type=oda_tip)
        room_type.save()

        return room_type

    @staticmethod
    def yeni_personel(personel_turu=1, unit='', personel_say=1, user=None):
        """
        Rastgele verileri ve parametre olarak verilen veriyi kullanarak
        yeni personel kaydı oluştururup kaydeder. Oluşturulan kayıtları liste olarak döndürür.

        Args:
            personel_turu (Personel): Personel türü
            unit (Unit) : Unit nesnesi
            personel_say : Oluşturulacak personel sayısı
            user : Personele atanacak user

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
            p.birim = unit
            p.gorev_suresi_baslama = (datetime.datetime.now() - datetime.timedelta(
                days=random.choice(range(1, 30))))
            p.goreve_baslama_tarihi = p.gorev_suresi_baslama

            p.gorev_suresi_bitis = (datetime.datetime.now() + datetime.timedelta(
                days=random.choice(range(1, 30))))

            p.kh_sonraki_terfi_tarihi = (datetime.datetime.now() + datetime.timedelta(
                days=random.choice(range(1, 30))))
            p.ga_sonraki_terfi_tarihi = (datetime.datetime.now() + datetime.timedelta(
                days=random.choice(range(1, 30))))
            p.em_sonraki_terfi_tarihi = (datetime.datetime.now() + datetime.timedelta(
                days=random.choice(range(1, 30))))

            p.kazanilmis_hak_derece = random.randint(1, 7)
            p.kazanilmis_hak_kademe = random.randint(1, 8)
            p.kazanilmis_hak_ekgosterge = random.randint(1000, 3000)

            p.gorev_ayligi_derece = random.randint(1, 7)
            p.gorev_ayligi_kademe = random.randint(1, 8)
            p.gorev_ayligi_ekgosterge = random.randint(1000, 3000)

            p.emekli_muktesebat_derece = random.randint(1, 7)
            p.emekli_muktesebat_kademe = random.randint(1, 8)
            p.emekli_muktesebat_ekgosterge = random.randint(1000, 3000)

            if user:
                p.user = user
            else:
                username = fake.slug(u'%s-%s' % (p.ad, p.soyad))
                user = new_user(username=username)
                p.user = user

            p.save()
            personel_list.append(p)
        return personel_list

    @staticmethod
    def yeni_okutman(personel, birim_no=''):
        """
        Rastgele verileri ve parametre olarak verilen veriyi kullanarak
        yeni okutman kaydı oluştururup kaydeder.

        Args:
            personel (list): Personel nesne listesi
            birim_no (str): Birim yoksis no

        Returns:
            okutman_list (list): Yeni okutman kaydı

        """
        okutman_list = []

        for person in personel:
            o = Okutman()
            o.ad = fake.first_name()
            o.soyad = fake.last_name()
            o.unvan = person.unvan
            o.birim_no = birim_no
            o.personel = person

            # duplicate data check
            try:
                o.save()
                okutman_list.append(o)
            except:
                pass
        return okutman_list

    @staticmethod
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

    def yeni_ogrenci(self, ogrenci_say=1, program=None, personel=None):
        """
        Rastgele veriler kullanarak yeni öğrenci kaydı oluştururup kaydeder.
        Oluşturulan kayıtları liste olarak döndürür.

        Args:
            ogrenci_say (int): Oluşturulacak ogrenci sayısı
            program (object): Ogrencinin kaydedilecegi program
            personel (object): Ogrencinin programdaki danisamani

        Returns:
            Ogrenci (list): Yeni öğrenci kaydı

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
            if program and personel:
                self.yeni_ogrenci_program(ogrenci=o, program=program, personel=personel)
        return ogrenci_list

    @staticmethod
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
        try:
            bolum = Unit.objects.filter(yoksis_no=yoksis_program.parent_unit_no)[0]
        except Exception as e:
            print(e.message)

        program_list = []

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

    @staticmethod
    def yeni_ders(program, personel, donem, ders_say=1):
        """
        Rastgele verileri ve parametre olarak verilen veriyi
        kullanarak yeni ders kaydı oluştururup kaydeder.
        Oluşturulan kayıtları liste olarak döndürür.

        Args:
            program (Program): Program nesnesi
            personel (Personel): Personel nesnesi
            donem (Donem) : Donem nesnesi
            ders_say : Oluşturulacak Ders sayısı

        Returns:
            Ders: Yeni ders listesi

        """
        yerel_kredi = random.choice([2, 2, 2, 2, 2, 3, 4, 4, 4, 4, 4, 4, 6, 6, 6, 8, 8])

        ders_list = []
        for i in range(ders_say):
            d = Ders()
            d.ad = fake.lecture()
            d.ders_dili = random.choice(["Turkce", "Turkce", "Turkce", "Ingilizce"])
            d.kod = ints(length=3)
            d.ects_kredisi = random.choice(
                [1, 2, 2, 2, 2, 2, 3, 4, 4, 4, 4, 4, 4, 5, 5, 6, 6, 6, 8, 8])
            d.yerel_kredisi = yerel_kredi
            d.uygulama_saati = yerel_kredi / 2
            d.teori_saati = yerel_kredi / 2
            d.program = program
            d.donem = donem
            d.ders_koordinatoru = personel
            d.save()
            ders_list.append(d)
        return ders_list

    @staticmethod
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
            Sube (list) : Yeni şube listesi

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

    @staticmethod
    def yeni_sinav(sube, sinav_say=1):
        """
        Rastgele verileri ve parametre olarak verilen veriyi
        kullanarak yeni sınav kaydı oluştururup kaydeder.
        Oluşturulan kayıtları liste olarak döndürür.

        Args:
            sube (Sube): Şube nesnesi
            sinav_say : Oluşturulacak sınav sayısı

        Returns:
            Sinav (list): Sinav nesne listesi

        """

        sinav_list = []
        for i in range(sinav_say):
            s = Sinav()
            d = sube.donem
            s.tarih = d.baslangic_tarihi + datetime.timedelta(
                random.randint(1, (d.bitis_tarihi - d.baslangic_tarihi).days))
            s.yapilacagi_yer = sube.ad
            s.tur = random.randint(1, 7)
            s.sube = sube
            s.ders = sube.ders
            s.save()
            sinav_list.append(s)
        return sinav_list

    @staticmethod
    def yeni_ogrenci_program(ogrenci, program, personel):
        """
        Rastgele verileri ve parametre olarak verilen verileri
        kullanarak yeni öğrenci programı kaydı oluştururup kaydeder.

        Args:
            ogrenci (Ogrenci): Öğrenci nesnesi
            personel (object): Personel nesnesi
            program (object): Program nesnesi

        Returns:
            OgrenciProgram: Yeni öğrenci program kaydı

        """
        try:
            op = OgrenciProgram()
            op.ogrenci_no = str(ints(11))
            op.giris_tarihi = datetime.datetime(int(program.yil), 10, 1)
            op.danisman = personel
            op.program = program
            op.ogrenci = ogrenci

            op.save()
            return op
        except Exception as e:
            print(e.message)

    @staticmethod
    def yeni_ogrenci_dersi(sube, ogrenci_program, donem=None):
        """
        Rastgele verileri ve parametre olarak verilen verileri
        kullanarak öğrenci ders kaydı oluştururup kaydeder.

        Args:
            sube (Sube): Şube nesnesi
            ogrenci_program (object): Öğrenci Programı nesnesi
            donem (object): Donem nesnesi

        Returns:
            OgrenciDersi: Yeni öğrenci ders kaydı

        """
        try:
            od = OgrenciDersi()
            od.alis_bicimi = random.choice([1, 2])
            od.sube = sube
            od.ogrenci_program = ogrenci_program
            od.ogrenci = ogrenci_program.ogrenci
            if donem:
                od.donem = donem

            od.save()
            return od
        except Exception as e:
            print(e.message)

    @staticmethod
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
        try:
            dk = DersKatilimi()
            dk.katilim_durumu = float(random.randint(50, 100))
            dk.ders = sube
            dk.ogrenci = ogrenci
            dk.okutman = okutman

            dk.save()
            return dk
        except Exception as e:
            print(e.message)

    @staticmethod
    def yeni_degerlendirme_notu(sinav, ogrenci_program):
        """
        Rastgele verileri ve parametre olarak verilen verileri
        kullanarak yeni değerlendirme notu kaydı oluşturup kaydeder.

        Args:
            sinav (Sinav): Sınav nesnesi
            ogrenci_program (OgrenciProgram): Öğrenci nesnesi

        Returns:
            DegerlendirmeNot: Yeni değerlendirme notu kaydı

        """

        try:
            sinav = Sinav.objects.get(sinav.key)
            ogrenci_program = OgrenciProgram.objects.get(ogrenci_program.key)
            dn = DegerlendirmeNot()
            dn.puan = random.randint(0, 100)
            dn.yil = str(sinav.tarih.year)
            dn.donem = sinav.ders.donem.ad
            dn.ogretim_elemani = sinav.sube.okutman.ad
            dn.sinav = sinav
            dn.ogrenci_no = ogrenci_program.ogrenci_no
            dn.ogrenci = ogrenci_program.ogrenci
            dn.ders = sinav.ders
            dn.save()
            return dn
        except Exception as e:
            print(e.message)

    @staticmethod
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

    @staticmethod
    def yeni_donem_danismani(donem, okutman, bolum):
        """
        Parametre olarak verilen verileri
        kullanarak ilgili döneme danışman kaydı oluştururup kaydeder.

        Args:
            donem (Donem): Dönem nesnesi
            okutman (Okutman): Okutman nesnesi
            bolum (Unitime): Unitime nesnesi

        Returns:
            DonemDanisman: Yeni dönem danışman kaydı

        """

        d = DonemDanisman()
        d.donem = donem
        d.okutman = okutman
        d.bolum = bolum

        d.save()
        return d

    def fake_data(self, donem_say=1, kampus_say=2, personel_say=50, okutman_say=30, program_say=1,
                  ders_say=24, sinav_say=3, sube_say=3, ogrenci_say=20):
        """
        Rastgele verileri ve parametre olarak verilen verileri kullanarak
        yeni okutman, program, ders, şube, sınav, borc ve ders katılımı kayıtları
        oluştururup kaydeder.

        Args:
            donem_say (int): Donem Sayisi
            kampus_say (int): Kampus Sayisi
            personel_say (int): Personel sayısı
            okutman_say (int): Okutman sayısı
            program_say (int): Program sayısı
            ders_say (int): Ders sayısı
            sube_say (int): Şube sayısı
            sinav_say (int): Sınav sayısı
            ogrenci_say (int): Öğrenci sayısı

        """
        import time

        # kampus_list = self.yeni_kampus(kampus_say=kampus_say)
        # print("Oluşturulan kampus listesi : %s\n" % kampus_list)
        # time.sleep(3)
        #
        # buildings, rooms = self.yeni_bina()
        # print("Oluşturulan bina listesi : %s\n" % buildings)
        # print("Oluşturulan oda listesi : %s\n" % rooms)

        donem_list = self.yeni_donem(donem_say=donem_say, guncel=True)
        print("Oluşturulan donem listesi : %s\n" % donem_list)
        time.sleep(3)

        kampus_list = self.yeni_kampus(kampus_say=kampus_say)
        print("Oluşturulan kampus listesi : %s\n" % kampus_list)
        time.sleep(3)

        buildings, rooms = self.yeni_bina()
        print("Oluşturulan bina listesi : %s\n" % buildings)
        print("Oluşturulan oda listesi : %s\n" % rooms)

        # yoksis uzerindeki program birimleri
        yoksis_program_list = random.sample(Unit.objects.filter(unit_type='Program'), program_say)
        print(
            "Oluşturulan program listesi : %s - %s\n" % (
                yoksis_program_list, len(yoksis_program_list)))
        time.sleep(3)

        # yoksis program listesinden program olustur
        for yoksis_program in yoksis_program_list:
            program = self.yeni_program(yoksis_program=yoksis_program)[0]
            print("Oluşturulan program : %s\n" % program)

            personel_list = self.yeni_personel(unit=yoksis_program, personel_say=personel_say)
            print("Oluşturulan personel listesi : %s\n" % personel_list)

            random_personel_list = random.sample(personel_list, okutman_say)
            # okutman olmayan personellerden okutman olustur.

            okutman_list = self.yeni_okutman(random_personel_list,
                                             birim_no=yoksis_program.yoksis_no)
            print("Oluşturulan okutman listesi : %s\n" % okutman_list)

            donem = random.choice(Donem.objects.filter(guncel=True))

            # donem ici danismanlik yapacak ogretim gorevlisi kaydı
            for okt in okutman_list:
                self.yeni_donem_danismani(donem, okt, okt.personel.birim)
                print(
                    "%s adlı okutman %s dönemi için %s danışmanları arasına eklendi.\n" % (
                        okt, donem,
                        okt.personel.birim))
            # Öğrencileri Oluştur
            ogrenci_liste = self.yeni_ogrenci(ogrenci_say=ogrenci_say, program=program,
                                              personel=random.choice(personel_list))
            print("Oluşturulan ogrenci listesi: %s\n" % ogrenci_liste)

            # programa ait dersler
            for dc in range(ders_say):
                personel = random.choice(personel_list)
                ders = self.yeni_ders(program, personel, donem)[0]
                print("%s programı için oluşturulan ders : %s\n" % (program, ders))

                # derse ait subeler
                for sc in range(sube_say):
                    okutman = random.choice(okutman_list)
                    sb = self.yeni_sube(ders, okutman)[0]
                    print("%s dersi için %s adlı okutman ile oluşturulan şube : %s\n" % (
                        ders, okutman, sb))

                    sinav_liste = self.yeni_sinav(sube=sb, sinav_say=sinav_say)
                    print("Oluşturulan sınav listesi : %s\n" % sinav_liste)

                    n = dc / (ders_say / 4) + 1

                    for ogrenci in random.sample(ogrenci_liste[0:75 * n], 70 * n):
                        personel = okutman.personel

                        # ogrencinin program, ders, devamsizlik, borc bilgileri
                        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci,
                                                                     program=program)

                        self.yeni_ogrenci_dersi(sb, ogrenci_program, donem)
                        print("%s adlı öğrenciye yeni ders atandı: %s\n" % (ogrenci, sb.ad))

                        self.yeni_ders_katilimi(sb, ogrenci, okutman)
                        print("%s adlı öğrenci için yeni ders katılım kaydı yapıldı.\n" % ogrenci)

                        self.yeni_borc(ogrenci, ders.donem)
                        print("%s adlı öğrenci için yeni borç kaydı yapıldı.\n" % ogrenci)

                        # ogrenci not bilgisi
                        for sinav in sinav_liste:
                            self.yeni_degerlendirme_notu(sinav, ogrenci_program)
                            print(
                                "%s sınavı için %s adlı öğrencinin değerlendirme notu girildi.\n" %
                                (sinav, ogrenci))
