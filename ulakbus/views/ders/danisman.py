# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
"""Danışman Modülü

İlgili İş Akışlarına ait sınıf ve metotları içeren modüldür.

Dönem bazlı danışman atanmasını sağlayan iş akışını yönetir.

"""

from pyoko import ListNode
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView, form_modifier
from ulakbus.models.ogrenci import Donem, DonemDanisman, Okutman
from ulakbus.models.auth import Unit
from collections import OrderedDict
from ulakbus.views.ders.ders import prepare_choices_for_model

class DonemDanismanForm(forms.JsonForm):
    """``DonemDanisman`` sınıfı için form olarak kullanılacaktır.

    """

    fields.Button("İleri")

class DonemDanisman(CrudView):
    """Dönem Danışman Atama İş Akışı

    Dönem Danışman Atama, aşağıda tanımlı iş akışı adımlarını yürütür.

    - Bölüm Seç
    - Öğretim Elemanlarını Seç
    - Kaydet
    - Kayıt Bilgisi Göster

     Bu iş akışında kullanılan metotlar şu şekildedir:

     Dönem Formunu Listele:
        Kayıtlı dönemleri listeler

     Bölüm Seç:
        Kullanıcının bölüm başkanı olduğu bölümleri listeler

     Öğretim Elemanlarını Seç:
        Seçilen bölümdeki öğretim elemanları listelenir.

     Kaydet:
        Seçilen dönem ve bölüm için seçilen danışman kayıtlarını yapar.

     Kayıt Bilgisi Göster:
        Seçilen öğretim elemanları, dönem ve bölüm bilgilerinden oluşturulan kaydın özeti
        gösterilir.
        Bu adımdan sonra iş akışı sona erer.

     Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model
     ``DonemDanisman`` modelidir. Meta.model bu amaçla kullanılmıştır.

     Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "DonemDanisman"

    def bolum_sec(self):

        unit = self.current.role.unit




    def danisman_sec(self):
        self.output("danisman_sec")

    def danisman_kaydet(self):
        self.output("danisman_kaydet")

    def kayit_bilgisi_ver(self):
        self.output("kayit_bilgisi_ver")