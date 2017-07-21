# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPEtkinlikButcePlani
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import Permission
from zengine.forms import JsonForm, fields
from zengine.models import BPMNWorkflow
from zengine.models import TaskInvitation
from zengine.models import WFInstance
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from pyoko import ListNode
from datetime import datetime, timedelta

YURTICI = _(
u"""Konaklama Faturası

Ulaşım Faturası

Maaş Bordrosu

Kayıt Ücreti **

Katılım Belgesi ve Çevirisi *

Uçak Biniş Kartları *

Bildiri Sunumu *

Kongre Sonuç Raporu *


(*) eğer varsa

(**) Başvuruda talep edildiyse""")

YURTDISI = _(u"Pasaport Giriş Çıkış Fotokopi")


class ButcePlanForm(JsonForm):
    class Meta:
        title = _(u"Bütçe Planı")

    class Butce(ListNode):
        talep_turu = fields.Integer(__(u"Talep Türü"), required=True,
                                    choices='bap_bilimseL_etkinlik_butce_talep_turleri')
        istenen_tutar = fields.Float(__(u"Talep Edilen Tutar"), required=True)

    ileri = fields.Button(_(u"İleri"))


class EtkinlikBilgiForm(JsonForm):
    class Meta:
        title = _(u"Etkinlik Bilgileri")
        exclude = ['basvuru_yapan']

    ileri = fields.Button(_(u"İleri"))


class BAPEtkinlikBasvuru(CrudView):

    class Meta:
        model = 'BAPEtkinlikProje'

    def etkinlik_bilgi_gir(self):
        form = EtkinlikBilgiForm(self.object, current=self.current)
        self.form_out(form)

    def butce_plani_olustur(self):
        form = ButcePlanForm()
        self.form_out(form)

    def evrak_goster(self):
        form = JsonForm(title=_(u"Gerekli Evraklar"))
        form.ileri = fields.Button(_(u"Anladım, Onaya Gönder"))
        if self.current.task_data['EtkinlikBilgiForm']['etkinlik_lokasyon'] == 2:
            form.help_text = YURTICI
        else:
            form.help_text = YURTDISI
        self.form_out(form)

    def onayla_ve_kaydet(self):
        """
        Bu adımda etkinlik başvurusu ve butce plani kaydedilir. Koordinasyon birimine task
        invitation yollanır.
        """
        etkinlik = BAPEtkinlikProje(**self.current.task_data['EtkinlikBilgiForm'])
        butceler = self.current.task_data['ButcePlanForm']['Butce']
        etkinlik.basvuru_yapan = self.current.user.personel.okutman
        etkinlik.blocking_save()
        for butce in butceler:
            butce['ilgili_proje_id'] = etkinlik.key
            BAPEtkinlikButcePlani(**butce).blocking_save()

        wf = BPMNWorkflow.objects.get(name='bap_etkinlik_basvuru_incele')
        perm = Permission.objects.get('bap_etkinlik_basvuru_incele.koordinasyon_birimi')
        today = datetime.today()
        for role in perm.get_permitted_roles():
            wfi = WFInstance(
                wf=wf,
                current_actor=role,
                task=None,
                name=wf.name,
                wf_object=etkinlik.key
            )
            wfi.data = dict()
            wfi.data['flow'] = None
            wfi.data['etkinlik_basvuru_id'] = etkinlik.key
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
            inv.title = wfi.wf.title
            inv.save()

    def basari_mesaji_goster(self):
        form = JsonForm(title=_(u"Başvurunuzu tamamladınız!"))
        form.help_text = _(u'Başvurunuz BAP birimine başarıyla iletilmiştir. '
                         u'Değerlendirme sürecinde size bilgi verilecektir.')
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

