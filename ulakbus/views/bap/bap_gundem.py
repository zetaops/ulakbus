# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import BAPProje
from zengine.views.crud import CrudView, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.komisyon_sonrasi_adimlar import KomisyonKarariSonrasiAdimlar, gundem_kararlari


class YeniGundemForm(JsonForm):
    class Meta:
        title = __(u"Yeni Gündem")
        include = ['gundem_aciklama', 'oturum_numarasi', 'oturum_tarihi', 'karar_metni']

    kaydet = fields.Button(__(u"Kaydet"))
    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class GundemDuzenleForm(JsonForm):
    class Meta:
        title = _(u"{} / {}  - Komisyon Kararı")
        exclude = ['etkinlik', 'proje', 'gundem_tipi', 'sonuclandi', 'karar']

    kaydet = fields.Button(_(u"Kaydet"), cmd='save')
    iptal = fields.Button(_(u"Geri Dön"), form_validation=False)


class KararOnaylamaForm(JsonForm):
    class Meta:
        title = __(u"Gündem Sonuç Karar Onaylama")

    onayla = fields.Button(__(u"Onayla"), cmd='onayla')
    geri_don = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class Gundem(CrudView):
    class Meta:
        model = "BAPGundem"

    def list(self, custom_form=None):
        self.current.task_data.pop('object_id', None)
        custom_form = JsonForm(current=self.current, title=_(u"Gündem Listesi"))
        custom_form.ekle = fields.Button(_(u"Yeni Gündem Oluştur"), cmd='yeni_gundem')
        CrudView.list(self, custom_form=custom_form)

    def gundem_tipi_kontrol(self):
        self.current.task_data['diger_gundem'] = (self.object.gundem_tipi == 10)

    def yeni_gundem_olustur(self):
        form = YeniGundemForm(self.object, current=self.current)
        form.gundem_tipi = fields.String(__(u"Gündem Tipi"),
                                         choices='bap_komisyon_gundemleri',
                                         default=10,
                                         readonly=True)
        self.form_out(form)

    def yeni_gundem_kaydet(self):
        self.set_form_data_to_object()
        self.object.blocking_save()

    def add_edit_form(self):
        form = GundemDuzenleForm(self.object, current=self.current)
        form.title = form.title.format(
            self.object.proje.ad,
            self.object.get_gundem_tipi_display() if self.object.proje else
            self.object.etkinlik.bildiri_basligi, self.object.get_gundem_tipi_display())
        help_text = _(u"Sonuçlandı") if self.object.sonuclandi else _(u"Sonuçlanmadı")
        form.help_text = (u"Gündem Durumu: {}").format(help_text)
        params = {'required': False,
                  'choices': gundem_kararlari[self.object.gundem_tipi]['kararlar']}
        params.update({'readonly': True,
                       'default': self.object.karar} if self.object.sonuclandi else {})

        form.gundem_karar = fields.String(__(u"Karar"), **params)
        self.form_out(_form=form)

    def gundem_sonuc_kontrol(self):
        td = self.current.task_data
        td['yeni'] = True if not self.object.sonuclandi and self.input['form'].get('gundem_karar',
                                                                                   None) else False

    def karar_onaylama(self):
        obj = self.object
        karar = dict(gundem_kararlari[obj.gundem_tipi]['kararlar'])[
            self.input['form']['gundem_karar']]
        form = KararOnaylamaForm(current=self.current)
        form.help_text = _(
            u"'{}' projesinin '{}' gündemi hakkında verdiğiniz karar '{}' dır. Bu karar "
            u"geri alınamaz! Bu işlemi onaylıyor musunuz?".
                format(obj.proje.ad,
                       obj.get_gundem_tipi_display(),
                       karar))

        self.form_out(form)

    def duzenleme_mesaji_olustur(self):
        self.object = self.object_form.deserialize(self.current.task_data['GundemDuzenleForm'])
        self.object.save()
        self.current.msg_box(title=_(u"İşlem Mesajı"),
                             msg=_(u"%s projesi başarı ile düzenlenmiştir.") % self.object.proje,
                             typ='info')

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
        del self.output['object'][u'Gündem Ekstra Bilgileri']

    def ilgili_methodu_cagir(self):
        karar = self.current.task_data['GundemDuzenleForm']['gundem_karar']
        self.object = self.object_form.deserialize(self.current.task_data['GundemDuzenleForm'])
        self.object.save()
        kararlar = gundem_kararlari[self.object.gundem_tipi]
        method = '_'.join([kararlar['tip_adi'], karar])
        getattr(KomisyonKarariSonrasiAdimlar(self.object, self.current.user), method)()

    def bilgilendirme(self):
        karar = self.current.task_data['GundemDuzenleForm'].pop('gundem_karar', '')
        self.object.karar = karar
        self.object.sonuclandi = True
        self.object.save()
        self.current.msg_box(title=_(u"İşlem Mesajı"),
                             msg=_(
                                 u"%s projesinin gündemi başarı ile sonuçlandırılmıştır. "
                                 u"İlgili kişiler bilgilendirilmiştir.") % self.object.proje,
                             typ='info')

    def confirm_deletion(self):
        form = JsonForm(title=_(u"Silme İşlemi"))
        form.help_text = _(u"Silme işlemini onaylıyor musunuz?")
        form.evet = fields.Button(_(u"Onayla"), cmd='delete')
        form.iptal = fields.Button(_(u"İptal"))
        self.form_out(form)

    @obj_filter
    def proje_turu_islem(self, obj, result):
        sonuc = {'name': _(u'Sonuçlandır/Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                 'show_as': 'button'}
        goster = {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}
        sil = {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'}
        result['actions'] = ([sonuc, goster, sil])
