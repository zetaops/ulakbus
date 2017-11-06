# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import AbstractRole
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import Role
from ulakbus.models import User
from zengine.forms import JsonForm, fields
from zengine.models import BPMNWorkflow
from zengine.models import TaskInvitation
from zengine.models import WFInstance
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from pyoko import ListNode
from datetime import datetime, timedelta


class EtkinlikBasvuruInceleForm(JsonForm):
    class Butce(ListNode):
        class Meta:
            title = "Bütçe"

        talep_turu = fields.Integer(__(u"Talep Türü"), required=True,
                                    choices='bap_bilimsel_etkinlik_butce_talep_turleri')
        istenen_tutar = fields.Float(__(u"Talep Edilen Tutar"), required=True)


class EtkinlikBasvuruInceleme(CrudView):
    """
    Koordinasyon birimi ve komisyon başkanının gelen bilimsel araştırma etkinlik başvurularını
    incelediği ve karar verdiği iş akışıdır. Koordinasyon birimi kendisine gelen görev üzerinden
    ya da etkinlik listeleme iş akışı üzerinden etkinlik inceleme iş akışını başlatır.
    Şeklen etkinlik başvurusunun uygun olduğuna karar verirse başvuruyu komisyon başkanına iletir.
    Komisyon başkanı başvuruyu değerlendirmek üzere bir komisyon üyesi seçer. Seçilen komisyon
    üyesine etkinlik başvuru değerlendirme görevi gönderilir.
    """

    class Meta:
        model = 'BAPEtkinlikProje'

    def __init__(self, current=None):
        super(EtkinlikBasvuruInceleme, self).__init__(current)
        # Task invitation oluşturulurken etkinlik id'si task data içine yerleştirilir. Eğer task
        # datada yoksa listeleme iş akışından gelindiği varsayılarak gelen inputtan alınır.
        key = self.current.task_data['etkinlik_basvuru_id'] = self.input.get(
            'object_id', False) or self.current.task_data.get('etkinlik_basvuru_id', False)
        self.object = BAPEtkinlikProje.objects.get(key)

    def incele(self):
        """
        Koordinasyon biriminin etkinlik başvurusunu incelediği adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        self.show()
        form = EtkinlikBasvuruInceleForm(title=_(u"Etkinlik Başvuru Detayları"))
        form.help_text = _(
            u"Bu projeyi daha sonra etkinlik listele iş akışından ulaşarak inceleyebilirsiniz.")
        form.reddet = fields.Button(_(u"Reddet"), cmd='red')
        form.daha_sonra_incele = fields.Button(_(u"Daha Sonra İncele"), cmd='daha_sonra_incele')
        form.reddet = fields.Button(_(u"Reddet"), cmd='red')
        form.komisyon = fields.Button(_(u"Komisyon Başkanına Gönder"), cmd='komisyon')
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def reddet_ve_bildirim_gonder(self):
        """
        Etkinlik başvurusunu yapan öğretim üyesine, başvurunun koordinasyon birimi tarafından
        reddedildiği bildiriminin gönderildiği adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        etkinlik.durum = 3
        etkinlik.blocking_save()
        role = Role.objects.filter(user=self.object.basvuru_yapan.personel.user)[0]
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        role.send_notification(title=_(u"Bilimsel Etkinlik Projesi Başvurusu"),
                               message=_(u"%s başlıklı bilimsel etkinlik projesi başvurunuz "
                                         u"koordinasyon birimi tarafından reddedilmiştir." %
                                         self.object.bildiri_basligi),
                               typ=1,
                               sender=sistem_user
                               )
        self.current.output['cmd'] = 'reload'

    def gorev_basligi_ekle(self):
        """
        Komisyon başkanına gösterilecek görevin başlığı değiştirilir.
        """
        etkinlik = BAPEtkinlikProje.objects.get(self.current.task_data['etkinlik_basvuru_id'])
        etkinlik.durum = 5
        etkinlik.blocking_save()
        wfi = WFInstance.objects.get(self.current.token)
        title = "%s | %s" % (etkinlik.__unicode__(), wfi.wf.title)
        self.current.task_data['INVITATION_TITLE'] = title

    def incele_kb(self):
        """
        Komisyon başkanının başvuruyu incelediği adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        self.show()
        form = EtkinlikBasvuruInceleForm(title=_(u"Etkinlik Başvuru Detayları"))
        form.daha_sonra_incele = fields.Button(_(u"Daha Sonra İncele"), cmd='daha_sonra_devam_et')
        form.reddet = fields.Button(_(u"Reddet"), cmd='red')
        form.komisyon = fields.Button(_(u"Komisyon Üyesi Ata"), cmd='komisyon_uyesi_ata')
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def daha_sonra_devam_et(self):
        """
        İş akışını uygun adıma taşıyarak ana sayfaya yöndlendirir.
        """
        self.current.output['cmd'] = 'reload'

    def komisyon_uyesi_ata(self):
        """
        Komisyon başkanının projeyi değerlendirmesi için komisyon üyesi seçtiği adımdır.
        Komisyon üyesi abstract rolüne sahip olan rollerin kullanıcıları listelenir. Daha sonra
        seçilen rol için proje değerlendirme görevi oluşturulup, ilgili rolün görev yöneticisine
        düşürülür.
        """
        form = JsonForm(title=_(u"Komisyon Üyesi Seç"))
        roller = Role.objects.filter(abstract_role=AbstractRole.objects.get(
            name='Bilimsel Arastirma Projesi Komisyon Uyesi'))
        choices = [(rol.key, rol.user.personel.__unicode__()) for rol in roller]
        form.komisyon_uye = fields.String(_(u"Komisyon Üyesi"), required=True, choices=choices)
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def komisyon_uyesine_davet_gonder(self):
        """
        Seçilen komisyon üyesinin görev yöneticisine proje değerlendirme iş akışının yerleştirildiği
        adımdır.
        """
        etkinlik_key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(etkinlik_key)
        rol_key = self.input['form']['komisyon_uye']
        role = Role.objects.get(rol_key)
        wf = BPMNWorkflow.objects.get(name='bap_komisyon_uyesi_etkinlik_basvuru_degerlendir')
        today = datetime.today()
        title = "%s | %s" % (etkinlik.__unicode__(), wf.title)
        wfi = WFInstance(
            wf=wf,
            current_actor=role,
            task=None,
            name=wf.name,
            wf_object=etkinlik_key
        )
        wfi.data = dict()
        wfi.data['flow'] = None
        wfi.data['etkinlik_basvuru_id'] = etkinlik_key
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
        etkinlik = BAPEtkinlikProje.objects.get(etkinlik_key)
        etkinlik.durum = 6
        etkinlik.blocking_save()
