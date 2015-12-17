# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models.auth import Unit
from ulakbus.models.personel import Personel
from ulakbus.models.ogrenci import Okutman
from .general import ints, gender, marital_status, blood_type, driver_license_class, id_card_serial, birth_date
from .general import fake
from random import random, randint

__author__ = 'Halil İbrahim Yılmaz'


def yeni_okutman():
    personel_list = Personel.objects.filter(unvan=1)
    random_personel = personel_list[randint(0, len(personel_list) - 1)]
    program_list = Unit.objects.filter(unit_type='Program')
    random_bolum = program_list[randint(0, len(program_list) - 1)]

    o = Okutman()
    o.ad = random_personel.ad
    o.soyad = random_personel.soyad
    o.unvan = random_personel.unvan
    o.birim_no = random_bolum.yoksis_no
    o.personel = random_personel
    o.save()
