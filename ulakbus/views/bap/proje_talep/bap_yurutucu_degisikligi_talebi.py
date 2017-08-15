# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPProje, BAPGundem, Personel, Okutman

from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class TalepForm(JsonForm):
    class Meta:
        include = ['yurutucu', 'aciklama']
        title = __(u"Yürütücü Değişikliği Talebi")
        help_text = __(u"Projeye yeni yürütücü atamak için  yürütücünün ismini yazıp ilerleyiniz")

    aciklama = fields.Text(__(u"Açıklama"), required=True)
    ilerle = fields.Button(_(u"İlerle"))


class YurutucuDegisikligi(CrudView):
    class Meta:
        model = "BAPProje"

    def kontrol(self):
        personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=personel)
        if BAPProje.objects.filter(yurutucu=okutman, durum__in=[3, 5]).count() == 0:
            self.current.task_data['cmd'] = 'bilgilendir'
            self.current.task_data['bilgilendirme'] = 'Devam eden projeniz yok.'
        elif 'kabul' in self.current.task_data:
            self.current.task_data['cmd'] = 'bilgilendir'
            self.current.task_data['bilgilendirme'] = self.current.task_data['kabul']
        elif 'red_msg' in self.current.task_data:
            self.current.task_data['cmd'] = 'bilgilendir'
            self.current.task_data['bilgilendirme'] = self.current.task_data['red_msg']
        elif 'bap_proje_id' not in self.current.task_data:
            self.current.task_data['cmd'] = 'proje_yok'

    def proje_sec(self):
        personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=personel)
        data = [(proje.key, proje.ad) for proje in BAPProje.objects.filter(yurutucu=okutman,
                                                                           durum__in=[3, 5])]

        form = JsonForm(title=_(u"Proje Seçiniz"))
        form.proje = fields.String(choices=data, default=data[0][0])
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def yurutucu_degisikligi_talebi(self):
        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']

        self.form_out(TalepForm(self.object, current=self.current))
        self.current.output["meta"]["allow_add_listnode"] = False

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
        proje.save()

    def bilgilendirme(self):
        form = JsonForm()
        form.title = self.current.task_data['bilgilendirme']['title']
        form.help_text = self.current.task_data['bilgilendirme']['msg']
        form.bitir = fields.Button(_(u"Tamam"), cmd='reload')
        self.form_out(form)

    def ana_sayfaya_yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def degisiklik_talebini_goruntule(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Proje: %s - Yürütücü Değişikliği Talebi") % proje.ad
        yeni_yurutucu = Okutman.objects.get(proje.yurutucu_talep['yurutucu_id'])
        obj_data = {"Şuanki Yürütücü": str(proje.yurutucu),
                    "Talep Edilen Yeni Yürütücü": str(yeni_yurutucu),
                    "Açıklama": proje.yurutucu_talep['yurutucu_aciklama']}
        self.output['object'] = obj_data
        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='onayla')
        form.reddet = fields.Button(_(u"Reddet"))
        self.form_out(form)

    def komisyona_gonder_aciklama(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        yeni_yurutucu = Okutman.objects.get(proje.yurutucu_talep['yurutucu_id'])
        form = JsonForm(title=_(u"Yürütücü Değişikliği Talebini Komisyona Yolla"))
        form.help_text = _(u"%s projesinin mevcut yürütücüsü olan %s 'nın yerine %s 'nın "
                           u"yürütücü olarak atanması talebini onaylayıp komisyona "
                           u"yollayacaksınız.") % (proje.ad, proje.yurutucu, yeni_yurutucu)

        form.komisyona_gonder = fields.Button(_(u"Komisyona Gönder"))
        form.onay_iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def onayla_gundeme_al(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        yeni_yurutucu = Okutman.objects.get(proje.yurutucu_talep['yurutucu_id'])
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
        gundem.gundem_aciklama = proje.yurutucu_talep['yurutucu_aciklama']
        gundem.save()

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        form.red_iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def yurutucuyu_bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        yeni_yurutucu = Okutman.objects.get(proje.yurutucu_talep['yurutucu_id'])
        if 'form' in self.input and 'red_gonder' in self.input['form']:
            title = "Talebiniz Koordinasyon Birimi Tarafından Reddedildi"
            msg = "%s projeniz için %s 'in yerine %s 'in yürütücü olarak atanması talebiniz " \
                  "reddedilmiştir. Red Açıklaması: %s" % (proje.ad, proje.yurutucu, yeni_yurutucu,
                                                          self.input['form']['red_aciklama'])
            self.current.task_data['red_msg'] = {'title': title, 'msg': msg}
        else:
            title = "Talebiniz Komisyonun Gündemine Alınmıştır"
            msg = "%s projeniz için %s 'in yerine %s 'in yürütücü olarak atanması talebiniz " \
                  "koordinasyon birimi tarafından kabul edilip Komisyon Gündemine alınmıştır." % (
                        proje.ad, proje.yurutucu, yeni_yurutucu)

            self.current.task_data['kabul'] = {'title': title, 'msg': msg}
