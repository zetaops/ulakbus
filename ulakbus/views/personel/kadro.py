# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from pyoko import form
from zengine.views.crud import CrudView, obj_filter

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Kadro


class KadroIslemleri(CrudView):
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Kadro'

        # viewlar arasi gecisi manuel yapacagiz.
        dispatch = False

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        object_actions = []

    class ObjectForm(JsonForm):
        class Meta:
            # durum alanini formdan cikar. kadrolar sadece sakli olarak kaydedilebilir.
            exclude = ['durum', ]

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
        super(KadroIslemleri, self).set_form_data_to_object()

        # durumu ne olursa olsun 1 (sakli) yap!..
        self.object.durum = 1

        # Kadroyu kaydet
        self.object.save()

    def sakli_izinli_degistir(self):
        """
        durum degerini 1 ve 2 arasinda degistir.
        1, sakli anlamina gelir,
        2, izinli anlamina gelir.

        sakliysa izinli yap 3 - 1 = 2
        izinliyse sakli yap 3 - 2 = 1

        """

        self.object.durum = 3 - self.object.durum
        self.save()

    @obj_filter
    def sakli_kadro(self, obj, result):
        """
        sakli kadro filtresi
        sakli kadro listesinde yer alan her bir item a Izinli Yap butonu ekle.

        :param obj: Kadro instance
        :param result: liste ogesi satiri
        :return: liste ogesi
        """
        if obj.durum == 1:
            result['actions'] = [
                {'name': 'Izinli Yap', 'cmd': 'sakli_izinli_degistir', 'mode': 'normal', 'show_as': 'button'}, ]
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
        if obj.durum == 2:
            result['actions'] = [
                {'name': 'Sakli Yap', 'cmd': 'sakli_izinli_degistir', 'mode': 'normal', 'show_as': 'button'}, ]
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
        if obj.durum in [1, 2]:
            result['actions'] = [
                {'name': 'Sil', 'cmd': 'delete', 'mode': 'bg', 'show_as': 'button'},
                {'name': 'Düzenle', 'cmd': 'form', 'mode': 'normal', 'show_as': 'button'},
            ]
        return result
