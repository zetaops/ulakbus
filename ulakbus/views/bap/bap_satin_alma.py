# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPButcePlani
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields


class ButceKalemleriForm(JsonForm):
    class Meta:
        title = __(u"Bütçe Kalemleri")
        inline_edit = ['sec']

    class Kalem(ListNode):
        sec = fields.Boolean(_(u"Seç"), type="checkbox")
        ad = fields.String(_(u"Tanımı/Adı"), readonly=True)
        adet = fields.Integer(_(u"Adet"), readonly=True)
        alim_kalemi_sartnamesi = fields.String(_(u"Alım Kalemi Şartnamesi"), readonly=True)
        genel_sartname = fields.String(_(u"Genel Şartname"), readonly=True)

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    tamam = fields.Button(_(u"Tamam"), cmd='tamam')


class BAPSatinAlma(CrudView):
    def butce_kalemleri_sec_goster(self):
        obj_id = self.input.get('object_id', None)
        if obj_id:
            self.current.task_data['obj_id'] = obj_id
        else:
            obj_id = self.current.task_data['obj_id']

        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje_id=obj_id)

        form = ButceKalemleriForm()
        for bp in butce_planlari:
            form.Kalem(
                sec=False,
                ad=bp.ad,
                adet=bp.adet,
                alim_kalemi_sartnamesi="",
                genel_sartname=""
            )

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def satin_alma_talebi_olustur(self):
        pass

    def satin_alma_talebi_kaydet(self):
        pass

