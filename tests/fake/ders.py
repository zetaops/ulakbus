# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.ogrenci import Program, Donem, Ders
from ulakbus.models.personel import Personel
from .general import fake, ints
from random import random, randint

__author__ = 'Halil İbrahim Yılmaz'


def yeni_ders():
    program_list = Program.objects.filter()
    term = Donem.objects.filter(guncel=True)[0]
    personel_list = Personel.objects.filter(unvan=1)

    for program in program_list:
        for i in range(randint(1, 9)):
            d = Ders()
            d.ad = fake.lecture()
            d.kod = ints(length=10)
            d.program = program
            d.donem = term
            d.ders_koordinatoru = personel_list[randint(0, len(personel_list) - 1)]
            d.save()

    print("Fake ders tanımlaması başarılı")
