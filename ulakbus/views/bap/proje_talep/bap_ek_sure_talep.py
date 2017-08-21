# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPProje, BAPGundem
from zengine.models import WFInstance, TaskInvitation
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
import json


class EkSureTalepForm(JsonForm):
    class Meta:
        title = __(u"{}/Ek Süre Talebi")

    ek_sure = fields.Integer(__(u"Ek Süre (Ay Olarak)"))
    aciklama = fields.Text(__(u"Açıklama"))
    gonder = fields.Button(__(u"Onaya Gönder"))


class TalepOnaylaForm(JsonForm):
    class Meta:
        title = __(u"Ek Süre Talep Onaylama")

    onayla = fields.Button(__(u"Onayla"), cmd='onayla')
    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class EkSureTalebi(CrudView):
    def ek_sure_talep_gir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = EkSureTalepForm(self.object, current=self.current)
        form.title = form.title.format(proje.ad)
        self.form_out(form)

    def talep_onaylama(self):
        self.current.task_data['ek_sure'] = self.input['form']['ek_sure']
        self.current.task_data['aciklama'] = self.input['form']['aciklama']
        form = TalepOnaylaForm(current=self.current)
        form.help_text = __(u"{} ay ek süre talebinde bulunmak üzeresiniz. Bu işlemi onaylıyor "
                            u"musunuz?".format(self.current.task_data['ek_sure']))
        self.form_out(form)

    def onaya_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.current.task_data['INVITATION_TITLE'] = "{} | {} | Ek Süre Talebi".format(
            proje.yurutucu.__unicode__(),
            proje.ad)
        proje.talep_uygunlugu = False
        proje.save()

    def talebi_goruntule(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Ek süre talebi") % \
                                      (proje.yurutucu, proje.ad)
        obj_data = {"Talep Edilen Süre(Ay olarak)": str(self.current.task_data['ek_sure']),
                    "Açıklama": self.current.task_data['aciklama']}
        self.output['object'] = obj_data
        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='iptal')
        self.form_out(form)

    def red_yazisi_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"), cmd='red')
        form.geri_don = fields.Button(_(u"Geri Dön"), cmd='geri_don', form_validation=False)
        self.form_out(form)

    def komisyon_aciklamasi(self):
        form = JsonForm(title=_(u"Komisyon Açıklaması"))
        form.komisyon_aciklama = fields.Text(_(u"Açıklama Yazınız"))
        form.yolla = fields.Button(_(u"Gönder"), cmd='onayla')
        form.geri_don = fields.Button(_(u"Geri Dön"), cmd='geri_don', form_validation=False)
        self.form_out(form)

    def komisyona_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        BAPGundem(proje=proje,
                  gundem_tipi=4,
                  gundem_aciklama=self.input['form']['komisyon_aciklama'],
                  gundem_ekstra_bilgiler=json.dumps({
                      'ek_sure': self.current.task_data['ek_sure'],
                      'aciklama': self.current.task_data['aciklama']})).save()

    def bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if 'red_aciklama' in self.input['form']:
            mesaj = "%s için yaptığınız %s aylık ek süre talebi " \
                    "reddedildi. RED Açıklaması: %s" % (
                        proje.ad, self.current.task_data['ek_sure'],
                        self.input['form']['red_aciklama'])
        else:
            mesaj = "Ek süre için bulunduğunuz talep kabul edilmiş olup, komisyonun gündemine " \
                    "alınmıştır."

        proje.talep_uygunlugu = True
        proje.save()
        proje.basvuru_rolu.send_notification(title="Koordinasyon Birimi Ek Süre Talep Kararı",
                                             message=mesaj,
                                             sender=self.current.user)

        self.current.output['msgbox'] = {
            'type': 'info',
            "title": _(u"İşlem Mesajı"),
            "msg": "Talep değerlendirmeniz başarılı ile gerçekleştirilmiştir. Proje yürütücüsü "
                   "{} değerlendirmeniz hakkında bilgilendirilmiştir.".format(
                proje.yurutucu.__unicode__())}

        wfi = WFInstance.objects.get(self.current.token)
        TaskInvitation.objects.filter(instance=wfi,
                                      role=self.current.role).delete()
