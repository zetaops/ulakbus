# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict

from ulakbus.models import Ogrenci
from ulakbus.views.reports.base import Reporter
from zengine.lib.utils import *

class OgrenciByGender(Reporter):
    HEADERS = ['', '']
    TITLE = 'Cinsiyete göre öğrenci sayıları'

    def get_objects(self):
        genders = self.convert_choices(Ogrenci().get_choices_for('cinsiyet'))
        result = []
        for val, num in Ogrenci.objects.distinct_values_of('cinsiyet').items():
            try:
                val = int(val)
            except:
                pass
            result.append((genders.get(val, val), num))
        return result


class OgrenciByBrithPlace(Reporter):
    HEADERS = ['', '']
    TITLE = 'Doğum yerine göre öğrenci sayıları'

    def get_objects(self):
        return [(val, num) for val, num in
                Ogrenci.objects.distinct_values_of('dogum_yeri').items()]


class OgrenciByBrithDate(Reporter):
    HEADERS = ['', '']
    TITLE = 'Doğum tarihine göre öğrenci sayıları'

    def get_objects(self):
        dates = defaultdict(lambda: 0)
        for val, num in Ogrenci.objects.distinct_values_of('dogum_tarihi').items():
            dates[solr_to_year(val)] += int(num)
        return dates.items()
