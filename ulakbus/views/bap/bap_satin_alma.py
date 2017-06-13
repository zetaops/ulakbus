# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import AbstractRole
from ulakbus.models import BAPButcePlani, BAPProje
from ulakbus.models import BAPSatinAlma
from ulakbus.models import Personel
from ulakbus.models import Role
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields
from ulakbus.settings import DATE_DEFAULT_FORMAT
import datetime


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
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    tamam = fields.Button(_(u"Tamam"), cmd='tamam')


class SatinAlmaTalebiForm(JsonForm):
    class Meta:
        title = __(u"Satın Alma Talebi")

    satin_alma_talep_adi = fields.String(u"Satın Alma Başlığı")
    yurutucu = fields.String(u"Proje Yürütücüsü")
    onay_tarih_sayi = fields.String(u"Onay Tarihi/Sayı")
    teklife_acilma_tarihi = fields.DateTime(u"Yayınlanma Tarihi")
    son_teklif_tarihi = fields.DateTime(u"Son Teklif Tarihi")
    ekleyen = fields.String(u"Ekleyen")
    aciklama = fields.Text(u"Açıklama", required=False)

    iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)
    geri = fields.Button(_(u"Bütçe Kalemlerine Dön"), cmd='geri', form_validation=False)
    kaydet = fields.Button(_(u"Kaydet"), cmd='kaydet')


class BAPSatinAlmaView(CrudView):
    def butce_kalemleri_sec_goster(self):
        obj_id = self.input.get('object_id', None)
        if obj_id:
            self.current.task_data['obj_id'] = obj_id
        else:
            obj_id = self.current.task_data['obj_id']

        msg = self.current.task_data.pop('uyari_mesaji', None)
        if msg:
            self.current.output['msgbox'] = {
                'type': 'error',
                "title": _(u"Eksik Seçim"),
                "msg": msg}
        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje_id=obj_id)

        form = ButceKalemleriForm()
        form.help_text = _(u"Satın alma talebi oluşturulacak bütçe kalemleri seçilmelidir.")
        for bp in butce_planlari:
            form.Kalem(
                sec=False,
                ad=bp.ad,
                adet=bp.adet,
                alim_kalemi_sartnamesi="",
                genel_sartname="",
                butce_plan_key=bp.key
            )

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def secimi_kontrol_et(self):
        kalemler = self.input['form']['Kalem']
        for kalem in kalemler:
            if kalem['sec']:
                self.current.task_data['cmd'] = 'gecerli'
                break
        else:
            self.current.task_data['uyari_mesaji'] = _(u"""Satın alma talebi oluşturmak için bütçe
            kalemi seçmediniz. Devam etmek için bütçe kalemi seçilmelidir.""")
            self.current.task_data['cmd'] = 'gecersiz'

    def satin_alma_talebi_olustur(self):
        obj_id = self.current.task_data['obj_id']
        proje = BAPProje.objects.get(obj_id)
        form = SatinAlmaTalebiForm()
        form.set_choices_of('yurutucu', choices=[(proje.yurutucu().key,
                                                  proje.yurutucu().__unicode__())])
        form.set_default_of('yurutucu', default=proje.yurutucu().key)
        ar = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi - Koordinasyon Birimi')
        role_list = Role.objects.filter(abstract_role=ar)
        personel_list = [Personel.objects.get(user=rr.user()) for rr in role_list]
        form.set_choices_of('ekleyen', choices=[(p.key, p.__unicode__()) for p in personel_list])
        form.set_default_of('ekleyen',
                            default=Personel.objects.get(user_id=self.current.user_id).key)

        self.form_out(form)

    def satin_alma_talebi_kaydet(self):
        satin_alma = BAPSatinAlma()
        kalemler = self.current.task_data['ButceKalemleriForm']['Kalem']
        talep_form = self.current.task_data['SatinAlmaTalebiForm']
        for kalem in kalemler:
            if kalem['sec']:
                satin_alma.ButceKalemleri(butce_id=kalem['butce_plan_key'])
        satin_alma.aciklama = talep_form['aciklama']
        satin_alma.ad = talep_form['satin_alma_talep_adi']
        satin_alma.teklife_acilma_tarihi = datetime.datetime.strptime(
            talep_form['teklife_acilma_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.teklife_kapanma_tarihi = datetime.datetime.strptime(
            talep_form['son_teklif_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.onay_tarih_sayi = talep_form['onay_tarih_sayi']
        satin_alma.ekleyen = Personel.objects.get(talep_form['ekleyen'])
        satin_alma.teklif_durum = 1

        satin_alma.blocking_save()

    def basari_mesaji_goster(self):
        form = JsonForm(title=_(u"Satın Alma Talebi"))
        form.help_text = _(u"Satın alma talebi başarıyla oluşturuldu.")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)