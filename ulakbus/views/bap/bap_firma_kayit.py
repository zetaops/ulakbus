# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext_lazy as __
from datetime import datetime
import hashlib


class FirmaKayitForm(JsonForm):
    class Meta:
        exclude = ['durum', 'Yetkililer']
        title = __(u'Firma Bilgileri')
        help_text = __(u'Lütfen kayıt işlemi için firma ve yetkili bilgilerinizi giriniz.')

    isim = fields.String(__(u"Yetkili Adı"), required=True)
    soyad = fields.String(__(u"Yetkili Soyadı"), required=True)
    k_adi = fields.String(__(u"Yetkili Kullanıcı Adı"), required=True)
    yetkili_e_posta = fields.String(__(u"Yetkili E-Posta"), required=True)
    kaydi_bitir = fields.Button(__(u"Kaydı Bitir"))


class BapFirmaKayit(CrudView):
    class Meta:
        model = 'BAPFirma'

    def kayit_formu_olustur(self):
        self.form_out(FirmaKayitForm(self.object, current=self.current))

    def kaydi_bitir(self):
        temp_password = hashlib.sha1(str(datetime.now())).hexdigest()
        form = self.input['form']
        user = User(name=form['isim'], surname=form['soyad'], username=form['k_adi'],
                    e_mail=form['e_posta'], password=temp_password)
        user.blocking_save()
        self.set_form_data_to_object()
        self.object.Yetkililer(yetkili=user)
        self.object.durum = 1
        self.object.blocking_save()

    def islem_mesaji_goster(self):
        firma_adi = self.input['form']['ad']
        self.current.output['msgbox'] = {"type": "info",
                                         "title": __(u'Firma Kaydı İşlem Mesajı'),
                                         "msg": __(
                                             u"%s adlı firmanız için kayıt başvurunuz alınmıştır."
                                             u" Koordinasyon birimi değerlendirmesinden sonra"
                                             u" başvuru sonucunuz hakkında bilgilendirileceksiniz."
                                             % firma_adi)}
