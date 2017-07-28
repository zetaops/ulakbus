# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import Okutman
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.models import BPMNWorkflow
from zengine.models import TaskInvitation
from zengine.models import WFInstance
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from datetime import datetime, timedelta


class HakemSecForm(JsonForm):
    class Meta:
        title = _(u"Hakem Seç")
    hakem = Okutman()
    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    tamam = fields.Button(_(u"Tamam"), cmd='tamam')


class KUEtkinlikBasvuruDegerlendirme(CrudView):
    class Meta:
        model = 'BAPEtkinlikProje'

    def __init__(self, current=None):
        super(KUEtkinlikBasvuruDegerlendirme, self).__init__(current)
        # Task invitation oluşturulurken etkinlik id'si task data içine yerleştirilir. Eğer task
        # datada yoksa listeleme iş akışından gelindiği varsayılarak gelen inputtan alınır.
        key = self.current.task_data['etkinlik_basvuru_id'] = self.input.get(
            'object_id', False) or self.current.task_data.get('etkinlik_basvuru_id', False)
        self.object = BAPEtkinlikProje.objects.get(key)

    def listele(self):
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        self.output['objects'] = [
            [_(u'Etkinlik Başlığı'), _(u'Başvuran'), _(u'Durum')]]
        list_item = {
            "fields": [etkinlik.bildiri_basligi, etkinlik.basvuru_yapan.__unicode__(),
                       etkinlik.durum],
            "actions": [
                {'name': _(u'Değerlendir'), 'cmd': 'degerlendir', 'mode': 'normal',
                 'show_as': 'button'},
                {'name': _(u'Hakem Seç'), 'cmd': 'hakem', 'mode': 'normal', 'show_as': 'button'},
            ],
            "key": key,
        }
        self.output['objects'].append(list_item)
        form = JsonForm(title=_(u"%s Etkinlik Başvuru Değerlendirmesi" % etkinlik.__unicode__()))
        form.daha_sonra_karar_ver = fields.Button(_(u"Daha Sonra Karar Ver"),
                                                  cmd='daha_sonra_karar_ver')
        self.form_out(form)

    def hakem_sec(self):
        form = HakemSecForm(current=self.current)
        self.form_out(form)
        self.output["meta"]["allow_add_listnode"] = False
        self.output['meta']['allow_actions'] = False
        self.output['meta']['allow_filters'] = False

    def hakeme_gonder(self):
        etkinlik = BAPEtkinlikProje.objects.get(self.current.task_data['etkinlik_basvuru_id'])
        hakem_id = self.input['form']['hakem_id']
        hakem = Okutman.objects.get(hakem_id)
        role = hakem.personel.user.role_set[0].role

        wf = BPMNWorkflow.objects.get(name='bap_etkinlik_basvuru_degerlendir')
        today = datetime.today()
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

    def daha_sonra_karar_ver(self):
        self.current.output['cmd'] = 'reload'


