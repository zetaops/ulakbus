# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import BAPGundem
from ulakbus.models import BAPProje

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __


class YeniGundemForm(JsonForm):
    class Meta:
        title = __(u"Yeni Gündem")

    proje = fields.String(__(u"Proje Seçiniz"))
    gundem_tipi = fields.String(__(u"Gündem Tipi"), choices='bap_komisyon_gundemleri', default=1)
    gundem_aciklama = fields.Text(__(u"Gündem Açıklaması"), required=False)
    oturum_numarasi = fields.Integer(__(u"Oturum Numarası"), required=False)
    oturum_tarihi = fields.Date(__(u"Oturum Tarihi"), required=False)
    kaydet = fields.Button(__(u"Kaydet"))


class Gundem(CrudView):
    class Meta:
        model = "BAPGundem"

    def list(self, custom_form=None):
        self.current.task_data.pop('object_id', None)
        custom_form = JsonForm(current=self.current, title=_(u"Gündem Listesi"))
        custom_form.ekle = fields.Button(_(u"Yeni Gündem Oluştur"), cmd='yeni_gundem')
        CrudView.list(self, custom_form=custom_form)

    def yeni_gundem_olustur(self):
        form = YeniGundemForm()
        form.set_choices_of('proje', prepare_choices_for_model(BAPProje))
        self.form_out(form)

    def yeni_gundem_kaydet(self):
        self.set_form_data_to_object()
        self.object.proje = BAPProje.objects.get(self.input['form']['proje'])
        self.object.blocking_save()

    def add_edit_form(self):
        form = JsonForm(self.object)
        form.title = _(u"%s / %s  - Komisyon Kararı") % (
            self.object.proje.ad, self.object.get_gundem_tipi_display()) if self.object.proje else (
            self.object.etkinlik.bildiri_basligi, self.object.get_gundem_tipi_display())
        form.exclude = ['etkinlik', 'proje', 'gundem_tipi', 'sonuclandi']
        form.kaydet = fields.Button(_(u"Kaydet"), cmd='save')
        form.iptal = fields.Button(_(u"İptal"), form_validation=False)
        self.form_out(_form=form)

    def show(self):
        CrudView.show(self)
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)
        self.output['object_title'] = _(u"%s / %s") % (self.object._proje_adi(),
                                                       self.object.get_gundem_tipi_display())
        sonuc = _(u"Sonuçlandı") if self.output['object'][u'Kararın Sonuçlandırılması'] == u'True' \
            else _(u"Sonuçlanmadı")

        self.output['object'][u'Kararın Sonuçlandırılması'] = sonuc

    def komisyon_kararini_ilet(self):
        self.object.proje.yurutucu.personel.user.send_notification(
            title=_(u"Komisyon Kararı"),
            message=_(u"%s adlı projenizin %s komisyon kararı Karar: %s") % (
                self.object.proje.ad,
                self.object.get_gundem_tipi_display(),
                self.input['form']['karar']),
            sender=self.current.role.user)

    def karar_sonrasi_adimlar(self):
        pass

    def bilgilendirme(self):
        self.object.sonuclandi = True
        self.object.save()
        self.current.msg_box(title=_(u"%s") % self.object.proje,
                             msg=_(u"%s projesi başarı ile sonuçlandırılmıştır") %
                             self.object.proje,
                             typ='info')

    @obj_filter
    def proje_turu_islem(self, obj, result):
        sonuc = {'name': _(u'Sonuç'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}
        goster = {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}
        sil = {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'}
        if obj.sonuclandi:
            result['actions'] = ([goster, sil])
        else:
            result['actions'] = ([sonuc, goster, sil])
