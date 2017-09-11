# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.views.bap.bap_etkinlik_basvuru_inceleme import EtkinlikBasvuruInceleForm

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
    """
    Komisyon üyesinin etkinlik başvurusu değerlendirdiği ya da değerlendirmesi için hakem seçtiği
    iş akışıdır. Seçilen hakeme etkinlik değerlendirme iş akışı gönderilir.
    """
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
        """
        Komisyon üyesinin kendisine gelen etkinlik başvurusunu liste şeklinde gördüğü adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        self.output['objects'] = [
            [_(u'Etkinlik Başlığı'), _(u'Başvuran'), _(u'Durum')]]
        list_item = {
            "fields": [etkinlik.bildiri_basligi, etkinlik.basvuru_yapan.__unicode__(),
                       etkinlik.durum],
            "actions": [
                {'name': _(u'Görüntüle'), 'cmd': 'goruntule', 'mode': 'normal',
                 'show_as': 'button'},
            ],
            "key": key,
        }
        self.output['objects'].append(list_item)
        form = JsonForm(title=_(u"%s Etkinlik Başvuru Değerlendirmesi" % etkinlik.__unicode__()))
        form.daha_sonra_karar_ver = fields.Button(_(u"Daha Sonra Karar Ver"),
                                                  cmd='daha_sonra_karar_ver')
        self.form_out(form)

    def goruntule(self):
        key = self.current.task_data['etkinlik_basvuru_id']
        self.show()
        form = EtkinlikBasvuruInceleForm(title=_(u"Etkinlik Başvuru Detayları"))
        form.daha_sonra_incele = fields.Button(_(u"Daha Sonra Değerlendir"),
                                               cmd='daha_sonra_karar_ver')
        form.hakeme_gonder = fields.Button(_(u"Hakeme Gönder"), cmd='hakem')
        form.degerlendir = fields.Button(_(u"Değerlendir"), cmd='degerlendir')
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def hakem_sec(self):
        """
        Komisyon üyesinin hakem seçtiği adımdır.
        """
        form = HakemSecForm(current=self.current)
        self.form_out(form)
        self.output["meta"]["allow_add_listnode"] = False
        self.output['meta']['allow_actions'] = False
        self.output['meta']['allow_filters'] = False

    def hakeme_gonder(self):
        """
        Bu adımda komisyon üyesinin seçtiği hakeme değerlendirme iş akışı gönderilir.
        """
        etkinlik = BAPEtkinlikProje.objects.get(self.current.task_data['etkinlik_basvuru_id'])
        hakem_id = self.input['form']['hakem_id']
        hakem = Okutman.objects.get(hakem_id)
        role = hakem.personel.user.role_set[0].role

        wf = BPMNWorkflow.objects.get(name='bap_etkinlik_basvuru_degerlendir')
        title = "%s | %s" % (etkinlik.__unicode__(), wf.title)
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
        wfi.data['hakem'] = True
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
        inv.title = title
        inv.save()

    def basari_mesaj_goster(self):
        """
        Komisyon üyesine işlem başarılı mesajının gösterildiği adımdır.
        """
        form = JsonForm(title=_(u"Hakem Seçimi Başarılı"))
        form.help_text = _(u"Seçtiğiniz hakeme basvuru değerlendirme daveti başarıyla gönderildi")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def daha_sonra_karar_ver(self):
        """
         Komisyon üyesini başvuruyu daha sonra değerlendirmek üzere anasayfaya yönlendiren adımdır.
        """
        self.current.output['cmd'] = 'reload'


