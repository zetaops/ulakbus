# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Kadro Islemleri WF adimlarini yurutur. WF 5 adimdan olusmaktadir.
#
# 1- Kadro listele
# 2- Sakli Kadro Ekle
# 3- Kaydet
# 4- Kadro Durumunu Sakli veya Izinli yap
# 5- Kadro Sil
#
#
# Bu WF, CrudView extend edilerek isletilmektedir. Adimlar arasi dispatch manuel sekilde yurutulmektedir.
# Her adim basina kullanilan metodlar su sekildedir:
#
# 1- Kadro Listele:
#    CrudView list metodu kullanilmistir. Liste ekraninda CrudView standart filtreleme ve arama ozellikleri
#    kullanilmaktadir. Listenin her bir ogesi icin object_actions filtreleri @obj_filter dekoratorleri
#    yardimiyla ozellestirilmistir.
#
#    Kadro islemleri kurallarina gore sadece sakli kadrolar eklenebilmekte veya
#    silinebilmektedir. Bu sebeple 'sil' eylemi sadece bu turdeki kadrolar icin aktifdir.
#
#    Sakli / Izinli Yap butonu ise sadece sakli veya izinli kadrolar icin gorunurdur.
#
#
# 2- Sakli Kadro Ekle
#    Kadrolar sadece ve sadece sakli olarak sisteme eklenebilirler. Bu amacla Crudview add_edit_form metodu
#    bastirilarak durum alani formdan cikarilmistir.
#
#
# 3- Kaydet
#    WF'nin 2. adimindan gelen data CrudView'in set_form_data_to_object metoduyla bir Kadro instance olusturularak
#    aktarilir.
#
#    Durum alani sakli (1) olarak sabitlenip kaydedilir.
#
#
# 4- Kadro Durumunu Sakli veya Izinli yap
#    Bunun icin ozel bir metod eklenmistir: sakli_izinli_degistir. Bu istenilen kadronun durumu arasinda gecis yapar.
#
#
# 5- Kadro Sil
#    Sadece durumu sakli (1) olan kadrolar silinebilir. Bunun icin kadro sil metodunda bu kontrol yapilir ve delete
#    metodu calistrilir.
#


from pyoko import form
from zengine.views.crud import CrudView, obj_filter

from zengine.lib.forms import JsonForm


class KadroIslemleri(CrudView):
    SAKLI = 1
    IZINLI = 2
    BOS = 3
    DOLU = 4

    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Kadro'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        object_actions = [
            # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        ]

    class ObjectForm(JsonForm):
        class Meta:
            # durum alanini formdan cikar. kadrolar sadece sakli olarak kaydedilebilir.
            exclude = ['durum', ]

            grouping = [
                {
                    "layout": "4",
                    "groups": [
                        {
                            "group_title": "Ünvan ve Derece",
                            "items": ['unvan', 'derece', 'unvan_kod'],
                            "collapse": True,
                        }
                    ]
                },
                {
                    "layout": "4",
                    "groups": [
                        {
                            "group_title": "Diğer",
                            "items": ['kadro_no', 'aciklama', 'birim_id']
                        }
                    ]
                }
            ]
            constraints = [
                {
                    'cons': [{'id': 'unvan_kod', 'cond': 'exists'}],
                    'do': 'change_fields', 'fields': [{'unvan': None}]
                },
                {
                    'cons': [{'id': 'unvan', 'cond': 'exists'}],
                    'do': 'change_fields', 'fields': [{'unvan_kod': None}]
                }
            ]

        save_edit = form.Button("Kaydet")

    #
    # ObjectForm birden cok view da farklilasiyorsa metod icinde bu sekilde kullanilmali.
    #
    # def kadro_ekle_form(self):
    #     self.object_form.exclude = ['durum',]
    #     self.form()
    #

    def kadro_kaydet(self):
        # formdan gelen datayi, instance a gecir.
        self.set_form_data_to_object()

        # durumu ne olursa olsun (sakli) yap!..
        self.object.durum = self.SAKLI

        # Kadroyu kaydet
        self.object.save()

        # isakisini bastan baslat
        self.reset()

    def kadro_sil(self):
        # sadece sakli kadrolar silinebilir
        assert self.object.durum != self.SAKLI, "attack detected, should be logged/banned"
        self.delete()

    def sakli_izinli_degistir(self):
        """
        durum degerini SAKLI ve IZINLI arasinda degistir.
        SAKLI: 1 degerine,
        IZINLI: 2, degerine sahiptir.

        sakliysa izinli yap 3 - SAKLI = IZINLI
        izinliyse sakli yap 3 - IZINLI = SAKLI

        """
        self.object.durum = 3 - self.object.durum
        self.object.save()

    @obj_filter
    def sakli_kadro(self, obj, result):
        """
        sakli kadro filtresi
        sakli kadro listesinde yer alan her bir item a Izinli Yap butonu ekle.

        :param obj: Kadro instance
        :param result: liste ogesi satiri
        :return: liste ogesi
        """
        if obj.durum == self.SAKLI:
            result['actions'].extend([
                {'name': 'Sil', 'cmd': 'delete', 'show_as': 'button'},
                {'name': 'Izinli Yap', 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'}])
        return result

    @obj_filter
    def izinli_kadro(self, obj, result):
        """
        sakli kadro filtresi
        sakli kadro listesinde yer alan her bir item a Sakli Yap butonu ekle.

        :param obj: Kadro instance
        :param result: liste ogesi satiri
        :return: liste ogesi
        """
        if obj.durum == self.IZINLI:
            result['actions'].append(
                    {'name': 'Sakli Yap', 'cmd': 'sakli_izinli_degistir', 'show_as': 'button'})
        return result

    @obj_filter
    def duzenlenebilir_veya_silinebilir_kadro(self, obj, result):
        """
        sakli kadro filtresi
        sakli kadro listesinde yer alan sakli veya izinli her bir item a Sil ve Duzenle butonu ekle.

        :param obj: Kadro instance
        :param result: liste ogesi satiri
        :return: liste ogesi
        """
        if obj.durum in [self.SAKLI, self.IZINLI]:
            result['actions'].extend([
                {'name': 'Düzenle', 'cmd': 'add_edit_form', 'show_as': 'button'},
            ])
        return result
