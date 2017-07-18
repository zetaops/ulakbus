# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import json

from ulakbus.models import BAPProje, BAPGundem, Personel, Okutman
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class EkSureTalepForm(JsonForm):
    class Meta:
        title = __(u"Ek Süre Talebi")
    ek_sure = fields.Integer(__(u"Ek Süre (Ay Olarak)"))
    aciklama = fields.Text(__(u"Açıklama"))
    gonder = fields.Button(__(u"Onaya Gönder"))
    iptal = fields.Button(__(u"İptal"), cmd='iptal', form_validation=False)


class EkSureTalebi(CrudView):

    def proje_id_kontrol(self):
        if 'bap_proje_id' in self.current.task_data:
            self.current.task_data['cmd'] = 'proje_id_var'
            proje_data = [(self.current.task_data['bap_proje_id'],
                           BAPProje.objects.get(self.current.task_data['bap_proje_id']).ad)]
            self.current.task_data['proje_data'] = proje_data
        else:
            self.current.task_data['cmd'] = 'proje_id_yok'

    def kontrol(self):
        if 'bap_proje_id' not in self.current.task_data:
            personel = Personel.objects.get(user=self.current.user)
            okutman = Okutman.objects.get(personel=personel)
            data = [(proje.key, proje.ad) for proje in BAPProje.objects.filter(yurutucu=okutman)]
            if data:
                self.current.task_data['proje_data'] = data
            else:
                self.current.task_data['onaylandi'] = 1
                self.current.task_data['proje_yok'] = {
                    'msg': 'Yürütücüsü olduğunuz herhangi bir proje '
                           'bulunamadı. Size bağlı olan proje '
                           'olmadığı için ek süre talebinde '
                           'bulunamazsınız.',
                    'title': 'Proje Bulunamadı'}
        else:
            data = [(self.current.task_data['bap_proje_id'],
                     BAPProje.objects.get(self.current.task_data['bap_proje_id']).ad)]
            self.current.task_data['proje_data'] = data

        if 'onaylandi' not in self.current.task_data:
            self.current.task_data['onaylandi'] = 0

    def ek_sure_talep_gir(self):
        if 'red_aciklama' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['red_aciklama'],
                                 title=_(u"Talebiniz Reddedildi."),
                                 typ='warning')
            del self.current.task_data['red_aciklama']

        form = EkSureTalepForm(self.object, current=self.current)
        form.proje = fields.String(_(u"Proje Seçiniz"),
                                   choices=self.current.task_data['proje_data'],
                                   default=self.current.task_data['proje_data'][0][0])
        self.form_out(form)

    def onaya_gonder(self):
        if 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']
        self.current.task_data['ek_sure'] = self.input['form']['ek_sure']
        self.current.task_data['aciklama'] = self.input['form']['aciklama']
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.save()

    def ek_sure_talebi_goruntule(self):
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
        form.red_gonder = fields.Button(_(u"Gönder"))
        self.form_out(form)

    def komisyon_aciklamasi(self):
        form = JsonForm(title=_(u"Komisyon Açıklaması"))
        form.komisyon_aciklama = fields.Text(_(u"Açıklama Yazınız"))
        form.yolla = fields.Button(_(u"Yolla"))
        self.form_out(form)

    def komisyona_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 4
        gundem.gundem_aciklama = self.input['form']['komisyon_aciklama']
        gundem.gundem_ekstra_bilgiler = json.dumps({'ek_sure': self.current.task_data['ek_sure'],
                                                    'aciklama': self.current.task_data['aciklama']})
        gundem.save()
        proje.save()
        self.current.task_data['onaylandi'] = 1

    def bilgilendir(self):
        if 'red_aciklama' in self.input['form']:
            proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            proje.durum = 3
            proje.save()
            self.current.task_data['red_aciklama'] = "%s için yaptığınız %s aylık ek süre talebi " \
                                                     "reddedildi. RED Açıklaması: %s" % (
                proje.ad, self.current.task_data['ek_sure'], self.input['form']['red_aciklama'])
        else:
            self.current.task_data['onay'] = "Ek süre için bulunduğunuz talep kabul edilmiş " \
                                             "olup, komisyonun gündemine alınmıştır."

    def bilgilendirme(self):
        if 'proje_yok' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['proje_yok']['msg'],
                                 title=self.current.task_data['proje_yok']['title'])
        else:
            self.current.msg_box(msg=self.current.task_data['onay'], title=_(u"Talebiniz Kabul "
                                                                             u"Edildi."))
