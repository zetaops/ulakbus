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
from ulakbus.lib.common import aktivasyon_kodu_uret
from ulakbus.lib.common import ParolaSifirlama


class ParolamiUnuttum(CrudView):
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
        try:
            if self.current.task_data['msg']:
                mesaj_goster(self, self.current.task_data['title'])
        except KeyError:
            pass

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
        kullanici_adlari = [u.username for u in User.objects.filter()]
        self.current.task_data['bilgi_kontrol'] = self.input['form']['kullanici_adi'] in kullanici_adlari

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
        Gönderilecek e-postanın içeriği ve linki wf ismi ve aktivasyon kodu ile hazırlanır.
        """

        user = User.objects.get(username=self.input['form']['kullanici_adi'])
        self.current.task_data['e_posta'] = user.e_mail
        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        ParolaSifirlama(self.current.task_data["aktivasyon"]).set(user.key, 7200)
        self.current.task_data["message"] = 'http://dev.zetaops.io/#/%s/dogrulama=%s' \
                                            % (self.current.task_data['wf_name'],
                                               self.current.task_data["aktivasyon"])
