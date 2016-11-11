# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from ulakbus.lib.views import UlakbusView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.models import User
from zengine.lib.translation import gettext as _
from ulakbus.settings import DEMO_URL
from ulakbus.lib.common import aktivasyon_kodu_uret
from ulakbus.lib.common import ParolaSifirlama
from ulakbus.lib.common import kullanici_adi_var_mi


class ParolamiUnuttum(UlakbusView):
    """
    Kullanıcının parolasını sıfırlamak için bilgilerini girmesini ve
    birincil e-posta adreslerine doğrulama linki gönderilmesini sağlar.
    """

    class Meta:
        model = "User"

    def link_gecerliligi_kontrolu(self):
        """

        Eğer linkle başlatıldıysa, doğrulama linkinin
        geçerli olup olmadığı kontrol edilir.

        """
        self.current.task_data['kod'] = aktivasyon_kodu = self.current.input['model'].split('=')[1]

        self.current.task_data['kullanici_key'] = ParolaSifirlama(aktivasyon_kodu).get()

    def kullanici_adi_girisi(self):
        """

        Parolanın sıfırlanabilmesi için kullanıcıdan kullandığı kullanıcı adı
        istenir. Bu kullanıcı adına ait birincil e-posta adresine doğrulama
        linki gönderilecektir. Eğer gösterilecek bir mesaj varsa (yanlış
        kullanıcı adı girişi gibi) mesaj ekrana basılır.
        """
        if self.current.task_data.get('msg', None):
            self.mesaj_kutusu_goster(self.current.task_data.get('title', _(u"Hatalı Bilgi")))

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

        self.current.task_data['kullanici_adi'] = kullanici_adi = self.input['form'][
            'kullanici_adi']
        self.current.task_data['dogruluk'] = kullanici_adi_var_mi(kullanici_adi)
        if not self.current.task_data['dogruluk']:
            self.current.task_data['msg'] = _(
                u"Böyle bir kullanıcı bulunmamaktadır. Lütfen tekrar deneyiniz.")

    def kullanici_bilgisi_cache_koy_e_posta_hazirla(self):
        """
        Doğrulama linki gönderilecek kullanıcının keyi,
        oluşturulan aktivasyon kodu ile cache'e kaydedilir.
        Gönderilecek e-postanın içeriği ve linki wf ismi ve aktivasyon kodu ile hazırlanır.
        """

        user = User.objects.get(username=self.current.task_data['kullanici_adi'])
        self.current.task_data['e_posta'] = user.e_mail
        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()
        ParolaSifirlama(self.current.task_data["aktivasyon"]).set(user.key, 7200)

        self.current.task_data["message"] = "E-Posta adresinizi doğrulamak için aşağıdaki" \
                                            " linke tıklayınız:\n\n %s/#/%s/dogrulama=%s" % (
            DEMO_URL, self.current.task_data['wf_name'], self.current.task_data["aktivasyon"])

        self.current.task_data['subject'] = 'Ulakbüs Aktivasyon Maili'
