# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import datetime
import math
from faker import Factory
import random

__author__ = 'Ali Riza Keles'

fake = Factory.create(locale='tr')


def ints(length=1):
    r = []
    for x in range(0, length):
        r.append(str(random.choice(range(0, 10))))
    return ''.join(r)


def gender():
    # return random.choice(['Erkek', 'Kadin'])
    return random.choice([1, 2])


def marital_status(student=False):
    MARRIED = 1
    SINGLE = 2
    statuses = [MARRIED, SINGLE]
    extend = [SINGLE] * 4 if student else [MARRIED] * 2
    statuses.extend(extend)
    return random.choice(statuses)


def blood_type():
    types = ['A', 'B', 'AB', '0']
    return "%s RH%s" % (random.choice(types), random.choice(['+', '-']))


def driver_license_class():
    types = ['A1', 'A2', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'K']
    return random.choice(types)


def id_card_serial():
    # return "%s%02d" % (fake.random_letter().upper(), fake.random_int(1, 99))
    return ints(11)


def birth_date(student=False):
    age_range = range(17, 30) if student else range(26, 80)
    return datetime.datetime.now() - datetime.timedelta(
            days=random.choice(age_range) * 365 + random.choice(range(-120, 120)))


def create_fake_geo_data():
    # TODO generate lat,long that releated with fake.city() / fake.state() methods

    x0 = 39.91
    y0 = 32.83
    dec_lat = random.random() / 100
    dec_lon = random.random() / 100
    return [x0 - dec_lat, y0 - dec_lon]
