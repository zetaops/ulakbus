# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

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
