# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import json
from ulakbus.models import BAPProje, BAPGundem, Okutman
from zengine.models import WFInstance, TaskInvitation
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class TalepForm(JsonForm):
    class Meta:
        include = ['yurutucu', 'aciklama']
        title = __(u"Yürütücü Değişikliği Talebi")
        help_text = __(u"Lütfen projeye yeni yürütücü atamak için yürütücünün ismini yazıp "
                       u"ilerleyiniz.")

    aciklama = fields.Text(__(u"Açıklama"), required=True)
    ilerle = fields.Button(_(u"İlerle"))


class YurutucuDegisikligi(CrudView):
    class Meta:
        model = "BAPProje"

    def yurutucu_degisikligi_talebi(self):
        self.form_out(TalepForm(self.object, current=self.current))
        self.current.output["meta"]["allow_add_listnode"] = False

    def yurutucu_secim_kontrol(self):
        td = self.current.task_data
        td['yurutucu_var'] = self.input['form']['yurutucu_id'] is not None

    def secim_uyari_mesaji(self):
        self.current.output['msgbox'] = {
            'type': 'warning',
            "title": _(u"Hatalı Yürütücü Seçimi"),
            "msg": _("İşlem yapabilmek için yürütücü seçmeniz gerekmektedir.")}

    def koordinasyona_gonder_onay(self):
        self.current.task_data['yurutucu_aciklama'] = self.input['form']['aciklama']
        self.current.task_data['yeni_yurutucu_id'] = self.input['form']['yurutucu_id']
        yeni_yurutucu = Okutman.objects.get(self.input['form']['yurutucu_id'])
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(title=_(u"Yürütücü Değişikliği Talebi"))
        form.help_text = _(u"%s projesinin mevcut yürütücüsü olan %s 'nın yerine %s 'nın "
                           u"yürütücü olarak atanması talebinde "
                           u"bulunuyorsunuz.") % (proje.ad,
                                                  proje.yurutucu,
                                                  yeni_yurutucu)
        form.gonder = fields.Button(_(u"Gönder"))
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def talebi_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.yurutucu_talep = {'yurutucu_id': self.current.task_data['yeni_yurutucu_id'],
                                'yurutucu_aciklama': self.current.task_data['yurutucu_aciklama']}
        proje.talep_uygunlugu = False
        proje.save()

        self.current.task_data['INVITATION_TITLE'] = "{} | {} | Yürütücü Değişikliği Talebi".format(
            proje.yurutucu.__unicode__(),
            proje.ad)

    def degisiklik_talebini_goruntule(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Proje: %s - Yürütücü Değişikliği Talebi") % proje.ad
        yeni_yurutucu = Okutman.objects.get(self.current.task_data['yeni_yurutucu_id'])
        obj_data = {"Şuanki Yürütücü": str(proje.yurutucu),
                    "Talep Edilen Yeni Yürütücü": str(yeni_yurutucu),
                    "Açıklama": self.current.task_data['yurutucu_aciklama']}
        self.output['object'] = obj_data
        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='onayla')
        form.reddet = fields.Button(_(u"Reddet"))
        self.form_out(form)

    def komisyona_gonder_aciklama(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        yeni_yurutucu = Okutman.objects.get(self.current.task_data['yeni_yurutucu_id'])
        form = JsonForm(title=_(u"Yürütücü Değişikliği Talebini Komisyona Yolla"))
        form.help_text = _(u"%s projesinin mevcut yürütücüsü olan %s 'nın yerine %s 'nın "
                           u"yürütücü olarak atanması talebini onaylayıp komisyona "
                           u"yollayacaksınız.") % (proje.ad, proje.yurutucu, yeni_yurutucu)

        form.komisyona_gonder = fields.Button(_(u"Komisyona Gönder"))
        form.onay_iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def onayla_gundeme_al(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        yeni_yurutucu = Okutman.objects.get(self.current.task_data['yeni_yurutucu_id'])
        yeni_yurutucu.personel.user.send_notification(
            title=_(u"Yürütücü Değişikliği"),
            message=_(u"%s, %s projesi için sizi yürütücü olarak atama talebinde bulunmuş "
                      u"olup talep komisyon gündemine alınmıştır.") % (
                proje.yurutucu,
                proje.ad),
            sender=self.current.role.user)
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 8
        gundem.gundem_aciklama = self.current.task_data['yurutucu_aciklama']
        gundem.gundem_ekstra_bilgiler = json.dumps(
            {'yeni_yurutucu_id': self.current.task_data['yeni_yurutucu_id']})
        gundem.save()

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        form.red_iptal = fields.Button(_(u"İptal"), cmd='iptal',form_validation=False)
        self.form_out(form)

    def yurutucuyu_bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.talep_uygunlugu = True
        proje.save()
        yeni_yurutucu = Okutman.objects.get(self.current.task_data['yeni_yurutucu_id'])
        if 'form' in self.input and 'red_gonder' in self.input['form']:
            title = "Talebiniz Koordinasyon Birimi Tarafından Reddedildi"
            msg = "%s projeniz için %s 'in yerine %s 'in yürütücü olarak atanması talebiniz " \
                  "reddedilmiştir. Red Açıklaması: %s" % (proje.ad, proje.yurutucu, yeni_yurutucu,
                                                          self.input['form']['red_aciklama'])
        else:
            title = "Talebiniz Komisyonun Gündemine Alınmıştır"
            msg = "%s projeniz için %s 'in yerine %s 'in yürütücü olarak atanması talebiniz " \
                  "koordinasyon birimi tarafından kabul edilip Komisyon Gündemine alınmıştır." % (
                        proje.ad, proje.yurutucu, yeni_yurutucu)

        self.current.output['msgbox'] = {
            'type': 'info',
            "title": _(u"İşlem Mesajı"),
            "msg": "Talep değerlendirmeniz başarılı ile gerçekleştirilmiştir. Proje yürütücüsü "
                   "{} değerlendirmeniz hakkında bilgilendirilmiştir.".format(
                proje.yurutucu.__unicode__())}

        proje.basvuru_rolu.send_notification(title=title,
                                             message=msg,
                                             sender=self.current.user)
        wfi = WFInstance.objects.get(self.current.token)
        TaskInvitation.objects.filter(instance=wfi,
                                      role=self.current.role).delete()
