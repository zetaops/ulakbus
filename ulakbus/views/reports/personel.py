# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import six

from ulakbus.models import Personel
from ulakbus.views.reports.base import Reporter


class PersonelByGender(Reporter):
    HEADERS = ['', '']
    TITLE = 'Cinsiyete göre personel sayıları'

    def get_objects(self):
        genders = self.convert_choices(Personel().get_choices_for('cinsiyet'))
        result = []
        for val, num in Personel.objects.distinct_values_of('cinsiyet').items():
            try:
                val = int(val)
            except:
                pass
            result.append((genders.get(val, val) , num))
        return result

class PersonelByAkademikIdari(Reporter):
    HEADERS = ['', '']
    TITLE = 'Akademik / İdari Personel Sayısı'

    def get_objects(self):
        genders = self.convert_choices(Personel().get_choices_for('personel_turu'))
        result = []
        for val, num in Personel.objects.distinct_values_of('personel_turu').items():
            try:
                val = int(val)
            except:
                pass
            result.append((genders.get(val, val), num))
        return result
