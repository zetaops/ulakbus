# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import six

from ulakbus.models import *
from ulakbus.views.reports.base import Reporter


class PersonelByGender(Reporter):
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
    TITLE = 'Akademik / İdari Personel Sayısı'

    def get_objects(self):
        choices = self.convert_choices(Personel().get_choices_for('personel_turu'))
        result = []
        for val, num in Personel.objects.distinct_values_of('personel_turu').items():
            try:
                val = int(val)
            except:
                pass
            result.append((choices.get(val, val), num))
        return result

class Kadrolar(Reporter):
    TITLE = 'Genel Kadro Durumları'

    def get_objects(self):
        choices = self.convert_choices(Kadro().get_choices_for('durum'))
        result = []
        for val, num in Kadro.objects.distinct_values_of('durum').items():
            try:
                val = int(val)
            except:
                pass
            result.append((choices.get(val, val), num))
        return result

# class Izinler(Reporter):
#     TITLE = 'Personel İzin Durumu'
#
#     def get_objects(self):
#         result = []
#         for val, num in Izin.objects.filter():
#             try:
#                 val = int(val)
#             except:
#                 pass
#             result.append((choices.get(val, val), num))
#         return result
