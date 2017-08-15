# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPProje, BAPGundem, Personel, Okutman

from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


class ProjeIptal(CrudView):

    class Meta:
        model = 'BAPProje'

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

    def proje_iptal_talebi(self):
        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.show()
        self.output['object_title'] = _(u"Proje iptal talebi : %s") % self.object
        form = JsonForm()
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

    def bilgilendirme(self):
        form = JsonForm()
        form.title = self.current.task_data['bilgilendirme']['title']
        form.help_text = self.current.task_data['bilgilendirme']['msg']
        form.bitir = fields.Button(_(u"Tamam"), cmd='reload')
        self.form_out(form)

    def ana_sayfaya_yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def talebi_goruntule(self):
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.show()
        self.output['object_title'] = _(u"Proje iptal talebi : %s") % self.object
        self.output['object']['İptal Talep Açıklama'] = self.current.task_data['proje_iptal_aciklama']
        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='onayla')
        form.reddet = fields.Button(_(u"Reddet"))
        self.form_out(form)

    def komisyona_gonder_onay_ekrani(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form = JsonForm(title=_(u"Proje İptal Talebi Talebini Komisyona Yolla"))
        form.help_text = _(u"%s projesinin iptal talebini onaylayıp komisyona "
                           u"yollayacaksınız.") % proje.ad

        form.komisyona_gonder = fields.Button(_(u"Komisyona Gönder"))
        form.onay_iptal = fields.Button(_(u"İptal"), cmd='iptal')
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
        form.red_iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def yurutucuyu_bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if 'form' in self.input and 'red_gonder' in self.input['form']:
            title = "Talebiniz Koordinasyon Birimi Tarafından Reddedildi"
            msg = "%s projeniz için bulunduğunuz iptal talebi reddedilmiştir. " \
                  "Red Açıklaması: %s" % (proje.ad, self.input['form']['red_aciklama'])
            self.current.task_data['red_msg'] = {'title': title, 'msg': msg}
        else:
            title = "Talebiniz Komisyonun Gündemine Alınmıştır"
            msg = "%s projeniz için bulunduğunuz iptal talebi koordinasyon birimi tarafından " \
                  "kabul edilip Komisyon Gündemine alınmıştır." % proje.ad

            self.current.task_data['kabul'] = {'title': title, 'msg': msg}
