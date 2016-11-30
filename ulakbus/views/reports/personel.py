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
import datetime
from zengine.lib.translation import gettext_lazy


class PersonelByGender(Reporter):
    TITLE = gettext_lazy(u'Cinsiyete göre personel sayıları')

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
    TITLE = gettext_lazy(u'Akademik / İdari Personel Sayısı')

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
    TITLE = gettext_lazy(u'Genel Kadro Durumları')

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


class TerfisiTikananPersonel(Reporter):
    TITLE = gettext_lazy(u"Terfisi Tıkanan Personel Listesi")

    def get_objects(self):
        """
        Terfisi Tikanan Personel icin kriterlerimiz:
            - gorev_ayligi_derecesi, kadro_derecesine esit olmali
            - gorev_ayligi_kademesi 3 ten buyuk olmalidir.

        Metodun amacı terfisi duran personelleri listelemektir. Burada
        görev aylığı kademesi 3 den yukarı olan personel listelenir.
        Sonrada bu personeller içerisinden kadro derecesi görev aylığı
        derecesine eşit olanlar seçilir. Örneğin bir personelin
        kadro derecesi ve görev aylığı derecesi 4 ise o personel 4/3 e
        kadar yükselebilir. 3 e düşemez. 4/4, 4/5 ... şeklinde gider.
        Bu yüzden personeller veritabanından çekilirken görev aylığı kademesi
        3 den yukarı olanlara bakıyoruz.

        Returns:
            personel_list (list): terfisi duran personel listesi

        """

        personel_list = []
        # todo: pyoko bir metod sagladiginda, raw yazilan bu sorguyu duzeltecegiz.
        p_query = Personel.objects.set_params(
            fq="{!frange l=0 u=0 incu=true}sub(gorev_ayligi_derece,kadro_derece)").filter(
            gorev_ayligi_kademe__gte=4)

        for p in p_query:
            personel_record = OrderedDict({})
            personel_record["TCK No"] = p.tckn
            personel_record["Ad"] = "%s %s" % (p.ad, p.soyad)
            personel_record["Personel Tür"] = str(p.personel_turu)
            personel_record["Kadro Derece"] = str(p.kadro.derece if p.kadro.derece else 0)

            personel_record["Görev Aylığı"] = "%i/%i" % (
                p.gorev_ayligi_derece, p.gorev_ayligi_kademe)

            personel_record["Kazanılmış Hak"] = "%i/%i" % (
                p.kazanilmis_hak_derece, p.kazanilmis_hak_kademe)

            personel_record["Emekli Müktesebat"] = "%i/%i" % (
                p.emekli_muktesebat_derece, p.emekli_muktesebat_kademe)

            personel_list.append(personel_record)

        return personel_list


class GorevSuresiBitenPersonel(Reporter):
    TITLE = gettext_lazy(u"Görev Süresi Dolan Personel Listesi")

    def get_objects(self):
        """ 
            Görev süresinin bitme durumu sadece akademik personel için geçerli
            bir durumdur. Personel modelindeki gorev_suresi_bitis alanındaki değerin
            bugünün datetime değerinden küçük olma durumuna bakılır.
        """
        simdi = datetime.date.today()
        bitis_tarihi = simdi + datetime.timedelta(days=120)

        # todo: add order_by
        personeller = Personel.objects.filter(
            gorev_suresi_bitis__lte=bitis_tarihi,
            personel_turu=1
        )
        personel_list = []
        for p in personeller:
            personel = OrderedDict({})
            personel["T.C. No"] = p.tckn
            personel["Ad"] = p.ad
            personel["Soyad"] = p.soyad
            personel["Birim"] = p.birim.name
            personel["Görev Süresi Başlangıç"] = p.gorev_suresi_baslama.strftime("%d.%m.%Y")
            personel["Görev Süresi Bitiş"] = p.gorev_suresi_bitis.strftime("%d.%m.%Y")
            personel["Göreve Başlama Tarihi"] = p.goreve_baslama_tarihi.strftime("%d.%m.%Y")
            personel_list.append(personel)

        return personel_list
