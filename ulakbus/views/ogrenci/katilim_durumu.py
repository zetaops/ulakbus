# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import Sube, OgrenciDersi, DersKatilimi
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy

__author__ = 'Ali Riza Keles'


class DevamsizlikForm(forms.JsonForm):
    class Meta:
        inline_edit = ['katilim_durumu', 'aciklama']
        title = gettext_lazy(u"Ders Seçim Formu")

    class Ogrenciler(ListNode):
        ogrenci_no = fields.String(gettext_lazy(u'Öğrenci No'))
        ad_soyad = fields.String(gettext_lazy(u'Ad Soyad'))
        katilim_durumu = fields.Integer(gettext_lazy(u'Katılım Durumu'))
        aciklama = fields.String(gettext_lazy(u'Açıklama'))
        ogrenci_key = fields.String('ogrenci_key', hidden=True)
        sube_key = fields.String('ders_key', hidden=True)


class OnizlemeForm(forms.JsonForm):
    class Meta:
        title = gettext_lazy(u"Katılım Durumu Bilgileri Önizleme Ekranı")

    class Ogrenciler(ListNode):
        ogrenci_no = fields.String(gettext_lazy(u'Öğrenci No'))
        ad_soyad = fields.String(gettext_lazy(u'Ad Soyad'))
        katilim_durumu = fields.Integer(gettext_lazy(u'Katılım Durumu'))
        aciklama = fields.String(gettext_lazy(u'Açıklama'))
        ogrenci_key = fields.String('ogrenci_key', hidden=True)
        sube_key = fields.String('ders_key', hidden=True)


class KatilimDurumu(CrudView):
    """ Ders Katılım Durumu

    Okutmanların öğrenci devamsızlıklarını sisteme girebilmesini
    sağlayan workflowa ait metotları barındıran sınıftır.

    Bu iş akışı 5 adımdan oluşur.

    Sube seç:
    Okutmanın kayıtlı olduğu şubelerden biri seçilir.

    Katılım Durumu Formu:
    Şubeye kayıtlı öğrencilerden bir form oluşturur. Yerinde düzenleme
    ile öğrenci devamsızlıkları girilir.

    Kontrol:
    Önceki adımda forma girilen bilgilerin doğruluğunun kontrol edilmesi
    için bilgileri bir tablo şeklinde ekrana getirir.

    Kaydet:
    Doğruluğu onaylanan bilgileri kaydeder.

    Bilgi Ver:
    Yapılan işlemin başarıyla sonuçlandığı ekrana basar.




    """

    class Meta:
        model = "DersKatilimi"

    def sube_sec(self):
        """
        Okutmanın kayıtlı olduğu şubelerden biri seçilir.

        """
        _form = forms.JsonForm(current=self.current, title=_(u"Şube Seçiniz."))
        _form.sube = fields.Integer(
            _(u"Sube Seçiniz"),
            choices=prepare_choices_for_model(Sube, okutman_id=self.get_okutman_key)
        )
        _form.sec = fields.Button(_(u"Seç"))
        self.form_out(_form)

    def katilim_durumu(self):
        """
        Seçile şubeye ait öğrencilerden  bir form oluşturur. Yerinde düzenleme
        ile öğrencilerin devamsızlıkları girilir.

        """

        _form = DevamsizlikForm(current=self.current, title=_(u"Ders Katılımı Giriş Formu"))

        try:
            sube_key = self.current.input['form']['sube']
            self.current.task_data["sube_key"] = sube_key
        except KeyError:
            sube_key = self.current.task_data["sube_key"]

        ogrenci_dersleri = OgrenciDersi.objects.filter(sube_id=sube_key)
        for ogrenci_dersi in ogrenci_dersleri:
            try:
                derse_katilim = DersKatilimi.objects.get(sube_id=sube_key,
                                                         ogrenci=ogrenci_dersi.ogrenci)
                katilim_durumu = derse_katilim.katilim_durumu
                aciklama = derse_katilim.aciklama
            except ObjectDoesNotExist:
                katilim_durumu = ""
                aciklama = ""

            _form.Ogrenciler(
                ad_soyad='%s %s' % (ogrenci_dersi.ogrenci.ad, ogrenci_dersi.ogrenci.soyad),
                ogrenci_no=ogrenci_dersi.ogrenci_program.ogrenci_no,
                katilim_durumu=katilim_durumu, ogrenci_key=ogrenci_dersi.ogrenci.key,
                sube_key=ogrenci_dersi.sube.key, aciklama=aciklama
            )

        _form.onizleme = fields.Button(_(u"Önizleme"), cmd="kontrol")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def kontrol(self):
        """
        Önceki adımda forma girilen bilgilerin doğruluğunun
        kontrol edilmesi için bilgileri bir tablo şeklinde ekrana
        getirir.

        """

        ogrenci_katilim_durumlari = self.current.input['form']['Ogrenciler']
        _form = OnizlemeForm(current=self.current)
        _form.duzenle = fields.Button(_(u"Geri Dön ve Düzenle"), flow="katilim_durumu")
        for katilim_durumu in ogrenci_katilim_durumlari:
            _form.Ogrenciler(
                ad_soyad=katilim_durumu['ad_soyad'],
                ogrenci_no=katilim_durumu['ogrenci_no'],
                katilim_durumu=katilim_durumu['katilim_durumu'],
                ogrenci_key=katilim_durumu['ogrenci_key'],
                sube_key=katilim_durumu['sube_key'], aciklama=katilim_durumu['aciklama']
            )
        _form.kaydet = fields.Button(_(u"Kaydet"))
        self.current.output["meta"]["allow_actions"] = False
        self.form_out(_form)

    def kaydet(self):
        """
        Doğruluğu onaylanan bilgileri kaydeder.

        """
        for katilim in self.current.input['form']['Ogrenciler']:
            ders_katilimi, is_new = DersKatilimi.objects.get_or_create(
                ogrenci_id=katilim['ogrenci_key'], sube_id=katilim['sube_key'])
            ders_katilimi.katilim_durumu = katilim['katilim_durumu']
            ders_katilimi.aciklama = katilim['aciklama']
            ders_katilimi.save()

    def bilgi_ver(self):
        """
        Yapılan işlemin başarıyla sonuçlandığı gösterir.

        """
        sube = Sube.objects.get(self.current.task_data['sube_key'])

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Devamsızlıklar Kaydedildi'),
            "msg": _(u'%s dersine ait öğrencilerin katılım bilgileri \
                           başarıyla kaydedildi') % sube.ders.ad}

    @property
    def get_okutman_key(self):
        """
        Harici okutman ve okutman kayıt key'lerinin ayrımını sağlayan metot.

        Returns:
            Okutman nesnesinin keyini

        """
        u = self.current.user
        return u.personel.okutman.key if u.personel.key else u.harici_okutman.okutman.key
