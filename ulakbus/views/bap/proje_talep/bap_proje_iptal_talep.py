# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPProje, BAPGundem
from zengine.models import WFInstance, TaskInvitation
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


class ProjeIptal(CrudView):
    class Meta:
        model = 'BAPProje'

    def proje_iptal_talebi(self):
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(current=self.current,
                        title=_(u"{} Projesi / Proje İptal Talebi".format(self.object.ad)))
        form.help_text = _(u"Lütfen proje iptal talebi için açıklama giriniz.")
        form.aciklama = fields.Text(_(u"Açıklama"))
        form.onay = fields.Button(_(u"Onaya Gönder"))
        self.form_out(form)

    def talebi_gonder_onay_ekrani(self):
        self.current.task_data['proje_iptal_aciklama'] = self.input['form']['aciklama']
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(title=_(u"Proje İptal Talebi"))
        form.help_text = _(u"%s projesini iptal için onaya yollayacaksınız. Yollamak istiyor "
                           u"musunuz ?") % proje.ad
        form.gonder = fields.Button(_(u"Gönder"))
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def talebi_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.current.task_data['INVITATION_TITLE'] = "{} | {} | Proje İptal Talebi".format(
            proje.yurutucu.__unicode__(),
            proje.ad)
        proje.talep_uygunlugu = False
        proje.save()

    def talebi_goruntule(self):
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(current=self.current,
                        title=_(u"{} Projesi / Proje İptal Talebi".format(self.object.ad)))
        form.help_text = _(u"İPTAL TALEBİ AÇIKLAMA: {}".format(
            self.current.task_data['proje_iptal_aciklama']))
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='onayla')
        form.reddet = fields.Button(_(u"Reddet"))
        self.form_out(form)

    def komisyona_gonder_onay_ekrani(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(title=_(u"Proje İptal Talebi Talebini Komisyona Yolla"))
        form.help_text = _(u"%s projesinin iptal talebini onaylayıp komisyona "
                           u"yollayacaksınız.") % proje.ad

        form.komisyona_gonder = fields.Button(_(u"Komisyona Gönder"))
        form.onay_iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)
        self.form_out(form)

    def komisyona_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 7
        gundem.gundem_aciklama = self.current.task_data['proje_iptal_aciklama']
        gundem.save()

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        form.red_iptal = fields.Button(_(u"İptal"), cmd='iptal', form_validation=False)
        self.form_out(form)

    def yurutucuyu_bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if 'form' in self.input and 'red_gonder' in self.input['form']:
            title = "Talebiniz Koordinasyon Birimi Tarafından Reddedildi"
            msg = "%s projeniz için bulunduğunuz iptal talebi reddedilmiştir. " \
                  "Red Açıklaması: %s" % (proje.ad, self.input['form']['red_aciklama'])
        else:
            title = "Talebiniz Komisyonun Gündemine Alınmıştır"
            msg = "%s projeniz için bulunduğunuz iptal talebi koordinasyon birimi tarafından " \
                  "kabul edilip Komisyon Gündemine alınmıştır." % proje.ad

        proje.talep_uygunlugu = True
        proje.save()
        proje.basvuru_rolu.send_notification(title=title,
                                             message=msg,
                                             sender=self.current.user)
        self.current.output['msgbox'] = {
            'type': 'info',
            "title": _(u"İşlem Mesajı"),
            "msg": "Talep değerlendirmeniz başarılı ile gerçekleştirilmiştir. Proje yürütücüsü "
                   "{} değerlendirmeniz hakkında bilgilendirilmiştir.".format(
                proje.yurutucu.__unicode__())}
        wfi = WFInstance.objects.get(self.current.token)
        TaskInvitation.objects.filter(instance=wfi, role=self.current.role).delete()
