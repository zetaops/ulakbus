# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import defaultdict

from pyoko import ListNode
from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, Personel, Okutman

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class ButceKalemleriForm(JsonForm):
    class Meta:
        title = __(u"Bütçe Kalemleri")
        inline_edit = ['sec']

    class Kalem(ListNode):
        class Meta:
            title = __(u"Bütçe Kalemleri")
        sec = fields.Boolean(_(u"Seç"), type="checkbox")
        ad = fields.String(_(u"Tanımı/Adı"), readonly=True)
        adet = fields.Integer(_(u"Adet"), readonly=True)
        alim_kalemi_sartnamesi = fields.String(_(u"Alım Kalemi Şartnamesi"), readonly=True)
        genel_sartname = fields.String(_(u"Genel Şartname"), readonly=True)
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    iptal = fields.Button(_(u"İptal Et ve Proje Listesine Dön"), cmd='iptal')
    ileri = fields.Button(_(u"Tamam"), cmd='ileri')


class ButceKalemGosterForm(JsonForm):
    class Meta:
        title = __(u"Seçilen Bütçe Kalemleri")

    class Kalem(ListNode):
        class Meta:
            title = __(u"Seçilen Bütçe Kalemleri")
        ad = fields.String(_(u"Tanımı/Adı"), readonly=True)
        adet = fields.Integer(_(u"Adet"), readonly=True)
        alim_kalemi_sartnamesi = fields.String(_(u"Alım Kalemi Şartnamesi"), readonly=True)
        genel_sartname = fields.String(_(u"Genel Şartname"), readonly=True)
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    butce_kalem_listesine_geri_don = fields.Button(_(u"Bütçe Kalem Listesine Geri Dön"),
                                                   cmd='geri_don')
    kaydet = fields.Button(_(u"Kaydet"), cmd='talep_gonder')



class BAPSatinAlmaTalep(CrudView):

    # Ogretim uyesi

    def butce_kalem_sec(self):
        self.current.task_data['bap_proje_id'] = 'WlRiJzMM4XExfmbgVyJDBZAUGg'
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        # todo satın almaya talebine uygun bütçe planlarını göstermek gerekli
        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje=proje)
        form = ButceKalemleriForm()
        for bp in butce_planlari:
            form.Kalem(
                sec=False,
                ad=bp.ad,
                adet=bp.adet,
                alim_kalemi_sartnamesi="",
                genel_sartname="",
                butce_plan_key=bp.key,
            )
        self.form_out(form)
        self.current.output['meta']['allow_actions'] = False
        self.current.output['meta']['allow_add_listnode'] = False

    def butce_kalem_goster(self):
        form = ButceKalemGosterForm()
        butce_kalemleri = self.input['form']['Kalem']
        for bk in butce_kalemleri:
            if bk['sec']:
                form.Kalem(**bk)
        self.form_out(form)
        self.current.output['meta']['allow_actions'] = False
        self.current.output['meta']['allow_add_listnode'] = False

    def butce_kalem_kaydet(self):
        pass

    def revizyon_mesaji_goster(self):
        pass

    def daha_sonra_devam_et(self):
        pass


    # Mali koordinator

    def satin_alma_talep_incele(self):
        pass

    def koordinasyon_birimi_gorevlisi_sec(self):
        pass

    def koordinasyon_birimine_gonder(self):
        pass

    def revizyon_gerekcesi_gir(self):
        pass

    def revizyon_talebi_gonder(self):
        pass


