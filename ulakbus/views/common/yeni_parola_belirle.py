# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from ulakbus.lib.views import UlakbusView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.lib.common import parola_kontrolleri
from ulakbus.models import User
from ulakbus.lib.common import ParolaSifirlama
from zengine.lib.translation import gettext as _


class YeniParolaBelirle(UlakbusView):
    """
    Kullanıcıların parola sıfırlamaları için e-posta adreslerini doğruladıklarında,
    yeni parola belirlemelerini sağlar.

    """

    def e_posta_dogrulama_mesaji_olustur(self):

        if self.current.task_data.get('msg', None):
            self.current.task_data['msg'] = """E-Posta adresiniz başarıyla doğrulanmıştır.
                                               Lütfen yeni parolanızı belirleyiniz."""
            self.current.task_data['title'] = 'E-Posta Adresi Doğrulama İşlemi'
            self.current.task_data['type'] = 'info'

    def yeni_parola_belirle(self):
        """
        Kullanıcıdan kurallara uygun yeni şifre belirlenmesi istenir. Eğer gösterilecek
        hatalı şifre mesajı varsa gösterilir.

        """

        if 'msg' in self.current.task_data:
            self.mesaj_kutusu_goster(self.current.task_data['title'],
                                     self.current.task_data['type'])

        _form = JsonForm(current=self.current, title=_(u'Yeni Parola Girişi'))
        _form.help_text = _(
u"""Kendi güvenliğiniz ve sistem güvenliği için yeni oluşturacağınız parola:

* Türkçe karakter içermemeli,
* 8 karakterden büyük olmalı,
* En az bir küçük harf, bir büyük harf, bir sayı ve bir özel karakter içermeli,
* Eski şifrenizle aynı olmamalıdır,
* Özel karakterler = ()[]{}!@#$%^&*+=-§±_~/|"><\.,:;≤≥
* Örnek parola = Ulakbüs3\*""")

        _form.yeni_parola = fields.String(_(u"Yeni parolanızı giriniz."), type="password")
        _form.yeni_parola_tekrar = fields.String(_(u"Yeni parolanızı tekrar giriniz."),
                                                 type="password")
        _form.onayla = fields.Button(_(u"Onayla"))
        self.form_out(_form)

    def yeni_parola_kontrol(self):
        """
        Yeni girilen parolanın kurallara uyup uymadığı kontrol edilir.
        Eğer uygunsa parola kaydetme adımına, uygun değilse hata mesajıyla
        birlikte bir önceki adıma gidilip şifresini yeniden belirlemesi
        istenir.

        """
        self.current.task_data['title'] = _(u'Hatalı Şifre')
        self.current.task_data['type'] = 'warning'

        yeni_parola = self.input['form']['yeni_parola']
        self.current.task_data['yeni_parola'] = yeni_parola
        yeni_parola_tekrar = self.input['form']['yeni_parola_tekrar']

        self.current.task_data['uygunluk'], self.current.task_data['msg'] = parola_kontrolleri(
            yeni_parola,
            yeni_parola_tekrar)

    def yeni_parola_kaydet(self):
        """
        Yeni girilen parola kaydedilmeden önce güvenlik nedeniyle
        kurallara uyup uymadığı bir daha kontrol edilir. Eğer uygunsa
        yeni parola kaydedilir. Uygun değilse ki bu beklenmeyen bir
        durumdur. Beklenmeyen hata adımına giderek bu hata mesajı
        kullanıcıya gösterilir.
        """
        kullanici = User.objects.get(self.current.task_data['kullanici_key'])
        kullanici.set_password(self.current.task_data['yeni_parola'])
        kullanici.save()
        ParolaSifirlama(self.current.task_data['kod']).delete()

    def parola_degisikligi_bilgilendir(self):
        """
        Yeni parolanın oluşturulma işlemi başarılı olduğunda kullanıcı
        başarılı işlem hakkında bilgilendirilir ve yeni oluşturduğu
        parola ile giriş yapması istenir.

        """
        self.current.task_data['show_logout_message'] = True
        self.current.task_data['logout_title'] = 'Parolanız Başarıyla Sıfırlandı'
        self.current.task_data['logout_message'] = """Yeni parolanızla giriş yapmak için
                                                    giriş ekranına yönlendiriliyorsunuz."""
