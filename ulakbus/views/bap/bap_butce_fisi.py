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
        always_blank = False

    class ButceKalemList(ListNode):
        class Meta:
            title = _(u"Bütçe Kalemleri")
        kod_adi = fields.String(_(u"Kod Adı"))
        ad = fields.String(_(u"Ad"))
        muhasebe_kod_genel = fields.Integer(_(u"Öğretim Üyesinin Seçtiği Muhasebe Kodu"),
                                            choices='bap_ogretim_uyesi_gider_kodlari')
        muhasebe_kod = fields.String(_(u"Muhasebe Kodu"),
                                     choices='analitik_butce_dorduncu_duzey_gider_kodlari')
        key = fields.String("Key", hidden=True)

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    kaydet = fields.Button(_(u"Kaydet ve Listele"), cmd='kaydet')


class BAPButceFisiView(CrudView):
    def butce_kalemlerini_goruntule(self):
        # proje_id = self.current.task_data['bap_proje_id']
        proje_id = 'WlRiJzMM4XExfmbgVyJDBZAUGg'
        butce_kalemleri = BAPButcePlani.objects.all(ilgili_proje_id=proje_id)
        form = ButceKalemleriForm(current=self.current, title=BAPProje.objects.get(proje_id).ad)
        for bk in butce_kalemleri:
            form.ButceKalemList(
                kod_adi=bk.kod_adi,
                ad=bk.ad,
                muhasebe_kod_genel=bk.muhasebe_kod_genel,
                muhasebe_kod=bk.muhasebe_kod,
                key=bk.key
            )
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)

    def butce_kalemlerini_kaydet(self):
        butce_kalemleri = self.input['form']['ButceKalemList']
        for bk in butce_kalemleri:
            butce_plani = BAPButcePlani.objects.get(bk['key'])
            if butce_plani.muhasebe_kod != bk['muhasebe_kod']:
                butce_plani.muhasebe_kod = bk['muhasebe_kod']
                butce_plani.blocking_save()

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def uyari_mesaji_goster(self):
        # form = JsonForm(title=_(u"Bütçe Fişi Onayı"))
        # form.help_text = _(u"Bütçe Kalemleri kodlarını kaydetmek istediğinize emin misiniz?")
        # form.geri = fields.Button(_(u"Geri"), cmd='geri')
        # form.onay = fields.Button(_(u"Onayla"), cmd='bitir')
        # self.form_out(form)
        proje_id = 'WlRiJzMM4XExfmbgVyJDBZAUGg'
        butce_kalemleri = BAPButcePlani.objects.all(ilgili_proje_id=proje_id)
        setattr(ButceKalemleriForm, 'iptal', fields.Button(_(u"Listeye Dön"), cmd='geri'))
        setattr(ButceKalemleriForm, 'kaydet', fields.Button(_(u"Bitir"), cmd='bitir'))
        setattr(ButceKalemleriForm.Meta, 'inline_edit', [])
        form = ButceKalemleriForm(current=self.current, title=BAPProje.objects.get(proje_id).ad)
        form.help_text = _(u"Bütçe kalemlerinin muhasebe kodlarını aşağıdaki gibi kaydettiniz. "
                           u"Düzenleme yapmak için 'Listeye Dön' işlemi tamamlamak için 'Bitir' "
                           u"butonlarını kullanabilirsiniz.")
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)
        setattr(ButceKalemleriForm, 'iptal', fields.Button(_(u"İptal"), cmd='iptal'))
        setattr(ButceKalemleriForm, 'kaydet', fields.Button(_(u"Kaydet ve Listele"), cmd='kaydet'))
        setattr(ButceKalemleriForm.Meta, 'inline_edit', ['muhasebe_kod'])