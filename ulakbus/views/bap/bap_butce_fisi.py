# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje

from pyoko import ListNode
from ulakbus.models import BAPButcePlani
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class ButceKalemleriForm(JsonForm):
    class Meta:
        inline_edit = ['muhasebe_kod']

    class ButceKalemList(ListNode):
        class Meta:
            title = _(u"Bütçe Kalemleri")
        kod_adi = fields.String(_(u"Kod Adı"))
        ad = fields.String(_(u"Ad"))
        muhasebe_kod = fields.String(_(u"Muhasebe Kodu"),
                                     choices='analitik_butce_dorduncu_duzey_gider_kodlari')

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    kaydet = fields.Button(_(u"Kaydet"), cmd='kaydet')
    onayla = fields.Button(_(u"Onayla"), style="btn-success", cmd='kaydet')


class BAPButceFisiView(CrudView):
    def butce_kalemlerini_goruntule(self):
        # proje_id = self.current.task_data['bap_proje_id']
        proje_id = 'WlRiJzMM4XExfmbgVyJDBZAUGg'
        butce_kalemleri = BAPButcePlani.objects.all(ilgili_proje_id=proje_id)
        form = ButceKalemleriForm(title=BAPProje.objects.get('proje_id').ad)
        for bk in butce_kalemleri:
            form.ButceKalemList(
                kod_adi=bk.kod_adi,
                ad=bk.ad,
                muhasebe_kod=bk.muhasebe_kod
            )
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)

    def butce_kalemlerini_kaydet(self):
        pass

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def uyari_mesaji_goster(self):
        form = JsonForm(title=_(u"Bütçe Fişi Onayı"))
        form.help_text = _(u"Bütçe Kalemleri kodlarını kaydetmek istediğinize emin misiniz?")
        form.geri = fields.Button(_(u"Geri"), cmd='geri')
        form.onay = fields.Button(_(u"Onayla"), cmd='bitir')
