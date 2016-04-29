# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import *
from ulakbus.views.reports.base import Reporter
from collections import OrderedDict


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
            result.append((genders.get(val, val), num))
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

class TerfisiDuranPersonel(Reporter):
    TITLE = "Terfisi Duran Personel Listesi"

    def get_objects(self):
        """
        Terfisi Duran Personel icin kriterlerimiz:
            - gorev_ayligi_derecesi, kadro_derecesine esit olmali
            - gorev_ayligi_kademesi 3 ten buyuk olmalidir.

        """

        personel_list = []
        # todo: pyoko bir metod sagladiginda, raw yazilan bu sorguyu duzeltecegiz.
        p_query = Personel.objects.raw("gorev_ayligi_kademe:[4 TO *] AND deleted: false",
                            fq="{!frange l=0 u=0 incu=true}sub(gorev_ayligi_derece,kadro_derece)")

        for p in p_query:

            personel_record = OrderedDict({})
            personel_record["TCK No"] = p.tckn
            personel_record["Ad"] = "%s %s" % (p.ad, p.soyad)
            personel_record["Personel Tür"] = p.personel_turu
            personel_record["Kadro Derece"] = p.kadro.derece

            personel_record["Görev Aylığı"] = "%i/%i" % (
                p.gorev_ayligi_derece, p.gorev_ayligi_kademe)

            personel_record["Kazanılmış Hak"] = "%i/%i" % (
                p.kazanilmis_hak_derece, p.kazanilmis_hak_kademe)

            personel_record["Emekli Müktesebat"] = "%i/%i" % (
                p.emekli_muktesebat_derece, p.emekli_muktesebat_kademe)

            personel_list.append(personel_record)

        return personel_list
