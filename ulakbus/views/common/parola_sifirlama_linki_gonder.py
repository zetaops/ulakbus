# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.models import User
from zengine.lib.translation import gettext as _
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster
from ulakbus.views.common.profil_sayfasi_goruntuleme import aktivasyon_kodu_uret
from zengine.lib.cache import PasswordReset


class ParolaSifirlamaLinkiGonder(CrudView):
    """
    Kullanıcının parolasını sıfırlamak için bilgilerini girmesini ve
    birincil e-posta adreslerine doğrulama linki gönderilmesini sağlar.
    """

    class Meta:
        model = "User"

    def kullanici_adi_girisi(self):
        """

        Parolanın sıfırlanabilmesi için kullanıcıdan kullandığı kullanıcı adı
        istenir. Bu kullanıcı adına ait birincil e-posta adresine doğrulama
        linki gönderilecektir. Eğer gösterilecek bir mesaj varsa (yanlış
        kullanıcı adı girişi gibi) mesaj ekrana basılır.
        """

        if self.current.task_data['msg']:
            mesaj_goster(self, self.current.task_data['title'])

        _form = JsonForm(current=self.current, title=_(u'Parola Sıfırlama'))
        _form.help_text = _(u"""Girdiğiniz kullanıcı adınıza kayıtlı birincil e-posta
                                adresinize parola sıfırlama linki gönderilecektir.""")
        _form.kullanici_adi = fields.String(_(u"Kullanıcı adınızı giriniz:"))
        _form.ilerle = fields.Button(_(u"Parola Sıfırlama Linki Gönder"))
        self.form_out(_form)

    def kullanici_adi_dogrulugu_kontrol(self):
        """
        Girilen kullanıcı adının veritabanında olup olmadığı kontrol edilir.
        Eğer hata yoksa doğrulama linki gönderilir, varsa hata mesajıyla
        birlikte bir önceki adıma gidilip hata mesajı gösterilir ve kullanıcıdan
        kullanıcı adını tekrar girmesi istenir.

        """

        user = User.objects.filter(username=self.input['form']['kullanici_adi'])
        self.current.task_data['bilgi_kontrol'] = False
        if user:
            self.current.task_data['bilgi_kontrol'] = True

    def hata_mesaji_olustur(self):
        """

        Girilen kullanıcı adına ait bir kullanıcı adı yoksa hata mesajı yaratılır
         ve kullanıcı adı girişi ekranına tekrar gidilerek hata mesajı gösterilir.
        """

        self.current.task_data['msg'] = _(u"Böyle bir kullanıcı bulunmamaktadır. Lütfen tekrar deneyiniz.")
        self.current.task_data['title'] = _(u"Hatalı Bilgi")

    def kullanici_bilgilerini_kaydet(self):
        """
        Doğrulama linki gönderilecek kullanıcının keyi, oluşturulan aktivasyon kodu ile cache'e kaydedilir.

        """

        user = User.objects.get(username=self.input['form']['kullanici_adi'])
        self.current.task_data['e_posta'] = user.e_mail
        self.current.task_data['bilgi'] = user.key
        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        PasswordReset(self.current.task_data["aktivasyon"]).set(self.current.task_data["bilgi"], 7200)
