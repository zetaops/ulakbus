# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import datetime, timedelta
from pyoko import ListNode
from ulakbus.lib.s3_file_manager import S3FileManager
from ulakbus.models import AbstractRole
from ulakbus.models import BAPProje, BAPButcePlani
from ulakbus.models import Role
from zengine.models import BPMNWorkflow
from zengine.models import TaskInvitation
from zengine.models import WFInstance
from zengine.views.crud import CrudView
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
        toplam_fiyat = fields.Float(_(u"Toplam Fiyat"), readonly=True)
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    iptal = fields.Button(_(u"İptal Et ve Proje Listesine Dön"), cmd='iptal', form_validation=False)
    ileri = fields.Button(_(u"Tamam"), cmd='ileri')


class ButceKalemGosterForm(JsonForm):
    class Meta:
        title = __(u"Seçilen Bütçe Kalemleri")

    class Kalem(ListNode):
        class Meta:
            title = __(u"Seçilen Bütçe Kalemleri")
        ad = fields.String(_(u"Tanımı/Adı"), readonly=True)
        adet = fields.Integer(_(u"Adet"), readonly=True)
        toplam_fiyat = fields.Float(_(u"Toplam Fiyat"), readonly=True)
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    butce_kalem_listesine_geri_don = fields.Button(_(u"Bütçe Kalem Listesine Geri Dön"),
                                                   cmd='geri_don')
    kaydet = fields.Button(_(u"Kaydet"), cmd='talep_gonder')


class TalepInceleForm(JsonForm):
    class Meta:
        title = __(u"Satın Alması Talep Edilen Bütçe Kalemleri")
        inline_edit = ['sec']

    Kalem = ButceKalemleriForm.Kalem

    daha_sonra_incele = fields.Button(_(u"Daha Sonra İncele"), cmd='daha_sonra_devam_et',
                                      form_validation=False)
    sartnameleri_indir = fields.Button(_(u"Şartnameleri İndir"), cmd='sartname')
    revizyon = fields.Button(_(u"Revizyona Gönder"), cmd='revizyon')
    calisan_ata = fields.Button(_(u"Çalışan Ata"), cmd='koordinasyon')


class KoordinasyonCalisaniSecForm(JsonForm):
    class Meta:
        title = __(u"Koordinasyon Birimi Çalışanı")

    calisan_rol = fields.String(_(u"Takip Edecek Personel"))
    satin_alma_turu = fields.Integer(_(u"Satın Alma Türü"), choices='bap_satin_alma_turleri')

    iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)
    gonder = fields.Button(_(u"Gönder"), cmd='gonder')


class BAPSatinAlmaTalep(CrudView):

    # Ogretim uyesi

    def butce_kalem_sec(self):
        hata_mesaji = self.current.task_data.pop('hata_mesaji', False)
        if hata_mesaji:
            self.current.output['msgbox'] = {'type': 'error',
                                             "title": _(u"Seçim Hatası"),
                                             "msg": hata_mesaji}
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje=proje, satin_alma_durum=5)
        form = ButceKalemleriForm()
        for bp in butce_planlari:
            form.Kalem(
                sec=False,
                ad=bp.ad,
                adet=bp.adet,
                toplam_fiyat=bp.toplam_fiyat,
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
        self.current.task_data['satin_almasi_talep_edilen_butce_kalemleri'] = self.input['form'][
            'Kalem']
        for bp in self.current.task_data['ou_secilen_butce_planlari']:
            bp_obj = BAPButcePlani.objects.get(bp)
            bp_obj.satin_alma_durum = 1
            bp_obj.blocking_save()

    def revizyon_mesaji_goster(self):
        form = JsonForm(title=_(u"Revizyon Talebi"))
        form.help_text = self.current.task_data['revizyon_mesaji']
        form.daha_sonra_devam_et = fields.Button(_(u"Daha Sonra Revize Et"),
                                                 cmd='daha_sonra_devam_et')
        form.revize_et = fields.Button(_(u"Revize Et"), cmd='revize_et')
        self.form_out(form)

    def daha_sonra_devam_et(self):
        self.current.output['cmd'] = 'reload'

    def kontrol_ou(self):
        secilen_butce_planlari = []
        for bp in self.input['form']['Kalem']:
            if bp['sec']:
                secilen_butce_planlari.append(bp['butce_plan_key'])

        if self.cmd != 'iptal' and not secilen_butce_planlari:
            self.current.task_data['cmd'] = 'hata'
            self.current.task_data['hata_mesaji'] = _(
                u"Yapmak istediğiniz işlem seçim yapmanızı gerektiriyor. Lütfen listeden seçim "
                u"yapınız.")
        else:
            self.current.task_data['ou_secilen_butce_planlari'] = secilen_butce_planlari


    # Mali koordinator

    def satin_alma_talep_incele(self):
        hata_mesaji = self.current.task_data.pop('hata_mesaji', False)
        onceki_adimda_secilen_butce_planlari = self.current.task_data.pop('secilen_butce_planlari',
                                                                          [])
        if hata_mesaji:
            self.current.output['msgbox'] = {'type': 'error',
                                             "title": _(u"Seçim Hatası"),
                                             "msg": hata_mesaji}
        form = TalepInceleForm()
        butce_kalemleri = self.current.task_data['satin_almasi_talep_edilen_butce_kalemleri']
        for i, bk in enumerate(butce_kalemleri):
                bk['sec'] = False
                form.Kalem(**bk)
        self.form_out(form)
        self.current.output['meta']['allow_actions'] = False
        self.current.output['meta']['allow_add_listnode'] = False
        self.current.task_data['toplam_bk'] = len(form.Kalem)

    def kontrol(self):
        secilen_butce_planlari = []
        for bp in self.input['form']['Kalem']:
            if bp['sec']:
                secilen_butce_planlari.append(bp['butce_plan_key'])

        if self.cmd not in ['revizyon', 'daha_sonra_devam_et'] and not secilen_butce_planlari:
            self.current.task_data['cmd'] = 'hata'
            self.current.task_data['hata_mesaji'] = _(
                u"Yapmak istediğiniz işlem seçim yapmanızı gerektiriyor. Lütfen listeden seçim "
                u"yapınız.")
        else:
            self.current.task_data['secilen_butce_planlari'] = secilen_butce_planlari

    def koordinasyon_birimi_gorevlisi_sec(self):
        abstract_role = AbstractRole.objects.get('UlB96RW78vE1iuEnoQ9JwBBHO9r')
        roller = Role.objects.filter(abstract_role=abstract_role)
        choices = [(r.key, "%s %s" % (r.user.personel.ad, r.user.personel.soyad)) for r in roller]
        form = KoordinasyonCalisaniSecForm()
        form.set_choices_of('calisan_rol', choices=choices)
        self.form_out(form)

    def koordinasyon_birimine_gonder(self):
        rol_key = self.input['form']['calisan_rol']
        role = Role.objects.get(rol_key)

        wf = BPMNWorkflow.objects.get(name='bap_tasinir_kodlari')
        today = datetime.today()
        wfi = WFInstance(
            wf=wf,
            current_actor=role,
            task=None,
            name=wf.name
        )
        wfi.data = dict()
        wfi.data['flow'] = None
        wfi.data['secilen_butce_planlari'] = self.current.task_data['secilen_butce_planlari']
        wfi.data['satin_alma_turu'] = self.input['form']['satin_alma_turu']
        wfi.data['bap_proje_id'] = self.current.task_data['bap_proje_id']
        wfi.pool = {}
        wfi.blocking_save()
        inv = TaskInvitation(
            instance=wfi,
            role=role,
            wf_name=wfi.wf.name,
            progress=30,
            start_date=today,
            finish_date=today + timedelta(15)
        )
        inv.title = wf.name
        inv.save()

        if self.current.task_data['toplam_bk'] - len(
            self.current.task_data['secilen_butce_planlari']) == 0:
            self.current.task_data['cmd'] = 'bitti'
        else:
            self.current.task_data['cmd'] = 'devam'
            for sbp in self.current.task_data['satin_almasi_talep_edilen_butce_kalemleri']:
                if sbp['butce_plan_key'] in self.current.task_data['secilen_butce_planlari']:
                    self.current.task_data['satin_almasi_talep_edilen_butce_kalemleri'].remove(sbp)

    def revizyon_gerekcesi_gir(self):
        form = JsonForm(title=_(u"Revizyon Gerekçesi"))
        form.gerekce = fields.Text(_(u"Gerekçe"))
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)
        form.gonder = fields.Button(_(u"Gönder"), cmd='revizyon')
        self.form_out(form)

    def revizyon_talebi_gonder(self):
        self.current.task_data['revizyon_mesaji'] = self.input['form']['gerekce']

    def sartname_indir(self):
        s3 = S3FileManager()
        keys = []
        for bt in self.current.task_data['secilen_butce_planlari']:
            butce_plani = BAPButcePlani.objects.get(bt)
            if butce_plani.teknik_sartname:
                keys.append(butce_plani.teknik_sartname.sartname_dosyasi)
        zip_name = "teknik-sartnameler"
        zip_url = s3.download_files_as_zip(keys, zip_name)
        self.set_client_cmd('download')
        self.current.output['download_url'] = zip_url
