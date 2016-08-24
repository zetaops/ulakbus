# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""
    İşten ayrılan personelin modelde arsiv alanı True yapılır.
    Modeldeki notlar alanı ile de işten ayrılan personel ile ilgili açıklama girme
    imkanı verilmiş olur.
"""

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import Personel

class IstenAyrilmaOnayForm(JsonForm):
    """
        Personel işten ayrılma işleminin onaylanması ve açıklama girilmesi
        amacıyla JsonForm class dan türetilmiş bir classdır.
    """
    class Meta:
        help_text = "Personel İşten ayrılma işlemini onaylıyormusunuz?"
        title = "Personel İşten Ayrılma"
        include = ["notlar"]

    devam_buton = fields.Button("Onayla")

class IstenAyrilma(CrudView):
    """
        Personel işten ayrılma wf adımlarının metodlarını içeren
        CrudView dan türetilmiş classdır.
    """
    class Meta:
        model = "Personel"

    def personel_id_kaydet(self):
        # Seçilmiş olan personelin id'si task data da saklanır
        self.current.task_data["personel_id"] = self.current.input["id"]

    def onay_form(self):
        # Onay form kullanıcıya gösteriliyor
        self.form_out(IstenAyrilmaOnayForm(self.object, current=self.current))

    def onayla(self):
        # Onaylanan işten ayrılma veritabanına işleniyor
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        personel.arsiv = True
        # Burada personelin işten ayrıldığına dair bir açıklama metni girişi yapılmaktadır.
        personel.notlar = self.current.input["form"]["notlar"]
        personel.save()

    # TODO: İşten ayrılan personelin üzerinde devam etmekte olan iş akışları için yapılacak
    def wf_devir(self):
        pass