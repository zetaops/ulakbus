# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.lib.common import parola_kontrolleri
from ulakbus.models import User
from ulakbus.lib.common import ParolaSifirlama
from zengine.lib.translation import gettext as _
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster

class YeniParolaBelirle(CrudView):
    """
    Kullanıcıların parola sıfırlamaları için e-posta adreslerini doğruladıklarında,
    yeni parola belirlemelerini sağlar.

    """
    def e_posta_dogrulama_mesaji_olustur(self):
        try:
            if self.current.task_data['wf_name']:
                self.current.task_data['msg'] = """E-Posta adresiniz başarıyla doğrulanmıştır.
                                                   Lütfen yeni parolanızı belirleyiniz."""
                self.current.task_data['title'] = 'E-Posta Adresi Doğrulama İşlemi'
                self.current.task_data['type'] = 'info'
        except KeyError:
            self.current.task_data['msg'] = None

    def yeni_parola_belirle(self):
        """
        Kullanıcıdan kurallara uygun yeni şifre belirlenmesi istenir. Eğer gösterilecek
        hatalı şifre mesajı varsa gösterilir.

        """

        if self.current.task_data['msg']:
            mesaj_goster(self, self.current.task_data['title'], self.current.task_data['type'])

        _form = JsonForm(current=self.current, title=_(u'Yeni Parola Girişi'))
        _form.help_text = _((u"Kendi güvenliğiniz ve sistem güvenliği için yeni oluşturacağınız parola:\n"
                             u"\n"
                             u"* Türkçe karakter içermemeli,\n"
                             u"* 8 karakterden büyük olmalı,\n"
                             u"* En az bir küçük harf, bir büyük harf, bir sayı ve bir özel karakter içermeli,\n"
                             u"* Özel karakterler = [\* & ^ % $ @ ! ? . : / > < ; ]\n"
                             u"* Örnek parola = Ulakbüs3\*\n"))
        _form.yeni_parola = fields.String(_(u"Yeni parolanızı giriniz."))
        _form.yeni_parola_tekrar = fields.String(_(u"Yeni parolanızı tekrar giriniz."))
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
        yeni_parola_tekrar = self.input['form']['yeni_parola_tekrar']

        parola_uygunluk, hata_mesaji = parola_kontrolleri(yeni_parola, yeni_parola_tekrar)

        self.current.task_data['uygunluk'] = parola_uygunluk
        if not parola_uygunluk:
            self.current.task_data['msg'] = hata_mesaji

    def yeni_parola_kaydet(self):
        """
        Yeni girilen parola kaydedilmeden önce güvenlik nedeniyle
        kurallara uyup uymadığı bir daha kontrol edilir. Eğer uygunsa
        yeni parola kaydedilir. Uygun değilse ki bu beklenmeyen bir
        durumdur. Beklenmeyen hata adımına giderek bu hata mesajı
        kullanıcıya gösterilir.
        """
        self.current.task_data['islem'] = False

        yeni_parola = self.input['form']['yeni_parola']
        yeni_parola_tekrar = self.input['form']['yeni_parola_tekrar']

        parola_uygunluk, hata_mesaji = parola_kontrolleri(yeni_parola, yeni_parola_tekrar)
        if parola_uygunluk:
            kullanici = User.objects.get(self.current.task_data['bilgi'])
            kullanici.set_password(self.input['form']['yeni_parola'])
            kullanici.save()
            ParolaSifirlama(self.current.task_data['kod']).delete()
            self.current.task_data['islem'] = True

    def parola_degisikligi_bilgilendir(self):
        """
        Yeni parolanın oluşturulma işlemi başarılı olduğunda kullanıcı
        başarılı işlem hakkında bilgilendirilir ve yeni oluşturduğu
        parola ile giriş yapması istenir.

        """
        kullanici = User.objects.get(self.current.task_data['bilgi'])
        _form = JsonForm(current=self.current, title=_(u'İşlem Bilgilendirme'))
        _form.help_text = _(u"""Sayın %s %s, parola sıfırlama işleminiz başarıyla gerçekleştirilmiştir.
                             Belirlediğiniz yeni parolanızla giriş yapmak için
                             'Giriş Ekranına Git' butonunu kullanabilirsiniz.""") % (kullanici.name, kullanici.surname)
        _form.giris_yap = fields.Button(_(u"Giriş Ekranına Git"))
        self.form_out(_form)