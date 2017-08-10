# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import Okutman
from zengine.forms import JsonForm
from zengine.models import BPMNWorkflow, WFInstance, TaskInvitation
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields
from datetime import datetime, timedelta
from pyoko import field


class HakemSecForm(JsonForm):
    class Meta:
        title = __(u"Hakem Ekle/Çıkar")

    class Hakemler(ListNode):
        class Meta:
            title = _(u"Hakem Adayları")
        ad = fields.String(_(u"Adı"), readonly=True)
        soyad = fields.String(_(u"Soyad"), readonly=True)
        email = fields.String(_(u"E-posta"), readonly=True)
        birim = fields.String(_(u"Birim"), readonly=True)
        durum = fields.Integer(_(u"Durum"), choices='bap_proje_hakem_degerlendirme_durum',
                               readonly=True)

    hakem = field.String(_(u"Hakem"))
    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    ekle = fields.Button(_(u"Ekle"), cmd='ekle')
    cikar = fields.Button(_(u"Çıkar"), cmd='cikar')
    bitir = fields.Button(_(u"Listedekilere Davet Gönder"), cmd='bitir')


class HakemlikDaveti(CrudView):
    """
        Koordinasyon biriminin hakem adaylarını seçerek adaylara davet gönderdiği iş akışı view
        kodudur. Basvuru Listeleme is akisindan baslatilir.
    """
    class Meta:
        model = "BAPProje"

    def hakemleri_sec(self):
        """
             Koordinasyon birimi davet gondermek istedigi hakem adaylarini tek tek secerek listeye
             ekler. Listeden cikarmak istediklerini de ayni sekilde secer ve cikar butonuyla
             listeden cikarir.

             Listeyi olusturduktan sonra, listedekilere davet gonder butonuna tiklayarak
             listedeki adaylara davet gonderir.
        """
        form = HakemSecForm()
        hakem_list = [(i.key, i.__unicode__()) for i in Okutman.objects.exclude(
            key=self.object.yurutucu().key)]
        form.set_choices_of('hakem', hakem_list)
        form.set_default_of('hakem', hakem_list[0][0])
        for pd in self.object.ProjeDegerlendirmeleri:
            form.Hakemler(
                ad=pd.hakem.okutman().ad,
                soyad=pd.hakem.okutman().soyad,
                email=pd.hakem.okutman().e_posta,
                birim=pd.hakem.okutman().birim().name,
                durum=pd.hakem_degerlendirme_durumu
            )
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def hakem_kaydet(self):
        """
            Hakem adayi zaten listeye eklenmisse, tekrar eklenmez.
        """
        for hakem in self.object.ProjeDegerlendirmeleri:
            if hakem.hakem() == Okutman.objects.get(self.input['form']['hakem']):
                break
        else:
            self.object.ProjeDegerlendirmeleri(
                hakem=Okutman.objects.get(self.input['form']['hakem']),
                hakem_degerlendirme_durumu=1
            )
            self.object.blocking_save()

    def hakem_cikar(self):
        for hakem in self.object.ProjeDegerlendirmeleri:
            if hakem.hakem().key == self.input['form']['hakem']:
                role = hakem.hakem().okutman().user().role_set[0].role
                task_invs = TaskInvitation.objects.filter(
                    role=role,
                    title='Bap Proje Degerlendirme')
                for ti in task_invs:
                    if ti.instance().data['bap_proje_id'] == self.object.key:
                        ti.blocking_delete()
                        role.send_notification(title=_(u"Proje Hakemlik Daveti"),
                                               message=_(u"""%s adlı projeyi değerlendirmek üzere
                                               koordinasyon birimi tarafından gönderilen hakemlik
                                               daveti hatalıdır. Davet görev yöneticinizden
                                               kaldırılmıştır. Eğer işlem yaptıysanız yaptığınız
                                               işlemler geçersiz olacaktır.""" % self.object.ad),
                                               typ=1,
                                               sender=self.current.user)
                hakem.remove()
        self.object.blocking_save()

    def davet_gonder(self):
        """
            Hakem adaylari sadece listeye yeni eklenmisse davet gonderilir. Coktan davet
            gonderilmis, davet reddedilmis ya da proje coktan degerlendirilmisse davet gonderilmez.
        """
        wf = BPMNWorkflow.objects.get(name='bap_proje_degerlendirme')
        today = datetime.today()
        for hakem in self.object.ProjeDegerlendirmeleri:
            if hakem.hakem_degerlendirme_durumu == 1:
                role = hakem.hakem().okutman().user().role_set[0].role
                wfi = WFInstance(
                    wf=wf,
                    current_actor=role,
                    task=None,
                    name=wf.name
                )
                wfi.data = dict()
                wfi.data['bap_proje_id'] = self.object.key
                wfi.data['davet_gonderen'] = self.current.user_id
                wfi.data['flow'] = None
                wfi.pool = {}
                wfi.blocking_save()
                role.send_notification(title=_(u"Proje Hakemlik Daveti"),
                                       message=_(u"""%s adlı projeyi değerlendirmek üzere koordinasyon
                                       birimi tarafından hakem olarak davet edildiniz. Görev
                                       yöneticinizden daveti kabul edip değerlendirebilir ya da daveti
                                       reddedebilirsiniz.""" % self.object.ad),
                                       typ=1,
                                       sender=self.current.user
                                       )
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
                hakem.hakem_degerlendirme_durumu = 2
        self.object.blocking_save()

    def davet_gonderildi_mesaj_goster(self):
        """
            Davet gonderildikten sonra koordinasyon birimine başarıyla davet gonderildigine dair
            mesaj gosterilir.
        """
        form = JsonForm(title=_(u"%s Adlı Proje Hakem Daveti" % self.object.__unicode__()))
        form.help_text = _(u"""Listeye eklediğiniz personellere hakemlik daveti gönderilmiştir.
        Davetler hakem adayları tarafından yanıtlandıklarında tarafınıza bilgilendirme yapılacaktır.
        """)
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def hakem_secim_kontrolu(self):
        self.current.task_data['hakem_sayisi'] = len(self.object.ProjeDegerlendirmeleri)

    def hakem_secilmedi_mesaj_goster(self):
        form = JsonForm(title=_(u"Hakem Seçilmedi"))
        form.help_text = _(u"""Lütfen hakem daveti göndermek için önce hakem listesinden hakem seçip ekle butonuna basınız.
                """)
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

