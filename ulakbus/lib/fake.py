# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import AbstractRole
from zengine.management_commands import *


class GenerateFakeData(Command):
    CMD_NAME = 'generate_fake_data'
    HELP = 'Generates fake data for ulakbüs'
    PARAMS = [

        {'name': 'donem_sayisi', 'type': int, 'default': 1,
         'help': 'Üretilecek dönem sayısı, varsayılan 1'},
        {'name': 'kampus_sayisi', 'type': int, 'default': 2,
         'help': 'Üretilecek kampüs sayısı, varsayılan 2'},
        {'name': 'personel_sayisi', 'type': int, 'default': 30,
         'help': 'Üretilecek personel sayısı, varsayılan 30'},
        {'name': 'okutman_sayisi', 'type': int, 'default': 20,
         'help': 'Üretilecek okutman sayısı, varsayılan 20'},
        {'name': 'program_sayisi', 'type': int, 'default': 1,
         'help': 'Üretilecek program sayısı, varsayılan 1'},
        {'name': 'ders_sayisi', 'type': int, 'default': 40,
         'help': 'Üretilecek ders sayısı, varsayılan 40'},
        {'name': 'sube_sayisi', 'type': int, 'default': 3,
         'help': 'Üretilecek şube sayısı, varsayılan 3'},
        {'name': 'sinav_sayisi', 'type': int, 'default': 3,
         'help': 'Üretilecek sınav sayısı, varsayılan 3'},
        {'name': 'ogrenci_sayisi', 'type': int, 'default': 30,
         'help': 'Üretilecek öğrenci sayısı, varsayılan 30'}

    ]

    def run(self):
        from tests.fake.fake_data_generator import FakeDataGenerator
        donem_say = int(self.manager.args.donem_sayisi)
        kampus_say = int(self.manager.args.kampus_sayisi)
        personel_say = int(self.manager.args.personel_sayisi)
        okutman_say = int(self.manager.args.okutman_sayisi)
        program_say = int(self.manager.args.program_sayisi)
        ders_say = int(self.manager.args.ders_sayisi)
        sube_say = int(self.manager.args.sube_sayisi)
        sinav_say = int(self.manager.args.sinav_sayisi)
        ogrenci_say = int(self.manager.args.ogrenci_sayisi)
        fake = FakeDataGenerator()
        fake.fake_data(donem_say=donem_say, kampus_say=kampus_say, personel_say=personel_say,
                       okutman_say=okutman_say,
                       program_say=program_say, ders_say=ders_say, sinav_say=sinav_say,
                       sube_say=sube_say,
                       ogrenci_say=ogrenci_say)

class GenerateFakeProgramData(Command):
    CMD_NAME = 'generate_fake_program_data'
    HELP = 'Generates fake program data for ulakbüs'
    PARAMS = [

        {'name': 'bolum_yoksis_no', 'type': int, 'required': True,
         'help': 'Bolum yoksis no girilmelidir.'},
        {'name': 'personel_sayisi', 'type': int, 'default': 30,
         'help': 'Üretilecek personel sayısı, varsayılan 30'},
        {'name': 'okutman_sayisi', 'type': int, 'default': 20,
         'help': 'Üretilecek okutman sayısı, varsayılan 20'},
        {'name': 'ders_sayisi', 'type': int, 'default': 40,
         'help': 'Üretilecek ders sayısı, varsayılan 40'},
        {'name': 'sube_sayisi', 'type': int, 'default': 3,
         'help': 'Üretilecek şube sayısı, varsayılan 3'},
        {'name': 'sinav_sayisi', 'type': int, 'default': 3,
         'help': 'Üretilecek sınav sayısı, varsayılan 3'},
        {'name': 'ogrenci_sayisi', 'type': int, 'default': 30,
         'help': 'Üretilecek öğrenci sayısı, varsayılan 30'},
        {'name': 'bina_sayisi', 'type': int, 'default': 4,
         'help': 'Üretilecek bina sayısı, varsayılan 4'}
    ]

    def run(self):
        from tests.fake.fake_data_generator import FakeDataGenerator
        bolum_yoksis_no = int(self.manager.args.bolum_yoksis_no)
        personel_say = int(self.manager.args.personel_sayisi)
        okutman_say = int(self.manager.args.okutman_sayisi)
        ders_say = int(self.manager.args.ders_sayisi)
        sube_say = int(self.manager.args.sube_sayisi)
        sinav_say = int(self.manager.args.sinav_sayisi)
        ogrenci_say = int(self.manager.args.ogrenci_sayisi)
        bina_say = int(self.manager.args.bina_sayisi)
        fake = FakeDataGenerator()
        fake.program_data_olustur(bolum_yoksis_no,personel_say=personel_say,
                       okutman_say=okutman_say,
                       ders_say=ders_say, sinav_say=sinav_say,
                       sube_say=sube_say,
                       ogrenci_say=ogrenci_say,
                       bina_say=bina_say)


class GenerateAbstractRoles(Command):
    CMD_NAME = 'generate_abstract_roles'
    HELP = 'Generates abstract roles'
    ROLE_LIST = [
        "Lisans Programı Öğrencisi - Aktif",
        "Lisans Programı Öğrencisi - Kayıt Dondurmuş",
        "Lisans Programı Öğrencisi - Kayıt Silinmiş",

        "Ön Lisans Programı Öğrencisi - Aktif",
        "Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş",
        "Ön Lisans Programı Öğrencisi - Kayıt Silinmiş",

        "Yüksek Lisans Programı Öğrencisi - Aktif",
        "Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş",
        "Yüksek Lisans Programı Öğrencisi - Kayıt Silinmiş",

        "Doktora Programı Öğrencisi - Aktif",
        "Doktora Programı Öğrencisi - Kayıt Dondurmuş",
        "Doktora Programı Öğrencisi - Kayıt Silinmiş",

        "Fakülte Dekanı",
        "Fakülte Dekan Sekreteri",
        "Fakülte Dekan Yardımcısı",
        "Fakülte Kurulu Başkanı (Dekan)",
        "Fakülte Kurulu Üyesi",
        "Fakülte Yönetim Kurulu Başkanı (Dekan)",
        "Fakülte Yönetim Kurulu Üyesi",
        "Fakülte Sekreteri",
        "Fakülte Etik Kurulu Başkanı",
        "Fakülte Etik Kurulu Üyesi",
        "Fakülte Öğrenci İşleri Şefi",
        "Fakülte Öğrenci İşleri Personeli",

        "Tıp Fakültesi Baş Koordinatörü",
        "Tıp Fakültesi Baş Koordinatör Yardımcısı",
        "Tıp Fakültesi Dönem Koordinatörü",
        "Tıp Fakültesi Eğitim Komisyonu Başkanı",
        "Tıp Fakültesi Eğitim Komisyonu Üyesi",

        "Yükselokul Müdürü",
        "Yükselokul Müdür Yardımcısı",
        "Yükselokul Kurulu Başkanı",
        "Yükselokul Kurulu Üyesi",
        "Yükselokul Yönetim Kurulu Başkanı",
        "Yükselokul Yönetim Kurulu Üyesi",
        "Yükselokul Sekreteri",
        "Yükselokul Öğrenci İşleri Şefi",
        "Yükselokul Öğrenci İşleri Personeli",
        "Yükselokul Muhasebe İşleri Şefi",
        "Yükselokul Muhasebe İşleri Personeli",
        "Yükselokul Birim Koordinatörü",

        "Bölüm Başkanı",
        "Bölüm Kurulu Başkanı",
        "Bölüm Kurulu Üyesi",
        "Bölüm Sekreteri",

        "Bilim Dalı Başkanı",
        "Bilim Dalı Üyesi",

        "Ana Bilim Dalı Başkanı",
        "Ana Bilim Dalı Üyesi",

        "Enstitü Müdürü",
        "Enstitü Müdür Yardımcısı",
        "Enstitü Kurulu Başkanı",
        "Enstitü Kurulu Üyesi",
        "Enstitü Yönetim Kurulu Başkanı",
        "Enstitü Yönetim Kurulu Üyesi",
        "Enstitü Sekreteri",
        "Enstitü Öğrenci İşleri Şefi",
        "Enstitü Öğrenci İşleri Personeli",
        "Enstitü Muhasebe İşleri Şefi",
        "Enstitü Muhasebe İşleri Personeli",

        "Öğretim Elemanı",
        # "Öğretim Üyesi",
        # "Öğretim Görevlisi",
        # "Araştırma Görevlisi",
        # "Okutman",
        # "Uzman",
        # "Çevirici",
        # "Eğitim-öğretim Planlamacısı",

        "Daire Başkanı",
        "Daire Şube Müdürü",
        "Şube Şefı",
        "Daire Personeli",

    ]

    def run(self):
        for role in self.ROLE_LIST:
            AbstractRole(name=role).save()