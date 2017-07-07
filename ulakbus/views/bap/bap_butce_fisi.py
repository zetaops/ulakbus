# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPButcePlani
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class ButceKalemleriForm(JsonForm):
    class Meta:
        title = _(u"Bütçe Kalemleri")
        inline_edit = ['muhasebe_kod']

    class ButceKalemList(ListNode):
        kod_adi = fields.String(_(u"Kod Adı"))
        ad = fields.String(_(u"Ad"))
        muhasebe_kod = fields.String(_(u"Muhasebe Kodu"),
                                     choices='analitik_butce_dorduncu_duzey_gider_kodlari')

    kaydet = fields.Button(_(u"Kaydet"), cmd='kaydet')


class BAPButceFisiView(CrudView):
    def butce_kalemlerini_goruntule(self):
        # proje_id = self.current.task_data['bap_proje_id']
        proje_id = 'WlRiJzMM4XExfmbgVyJDBZAUGg'
        butce_kalemleri = BAPButcePlani.objects.all(ilgili_proje_id=proje_id)
        form = ButceKalemleriForm()
        for bk in butce_kalemleri:
            form.ButceKalemList(
                kod_adi=bk.kod_adi,
                ad=bk.ad,
                muhasebe_kod=bk.muhasebe_kod
            )
        self.form_out(form)

    def butce_kalemlerini_kaydet(self):
        pass
