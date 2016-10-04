# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
from ulakbus.models import User
from zengine.lib.cache import Cache
from ulakbus.views.common import profil_sayfasi_goruntuleme as profil
from zengine.lib.translation import gettext as _


class ParolamiUnuttum(CrudView):
    """
    Kullanıcının parolasını sıfırlamak ve yeni parola oluşturmasını sağlar.
    """

    class Meta:
        model = "User"

    def bilgi_girisi(self):
        """

        Parolanın sıfırlanabilmesi için kullanıcıdan kullandığı kullanıcı adı
        istenir. Bu kullanıcı adına ait birincil e-posta adresine doğrulama
        linki gönderilecektir. Eğer gösterilecek bir mesaj varsa (yanlış
        kullanıcı adı girişi gibi) mesaj ekrana basılır.
        """

        if self.current.task_data['msg']:
            profil.mesaj_goster(self, self.current.task_data['title'])

        _form = JsonForm(current=self.current, title=_(u'Parola Sıfırlama'))
        _form.help_text = _(u"""Girdiğiniz kullanıcı adınıza kayıtlı birincil e-posta
                                adresinize parola sıfırlama linki gönderilecektir.""")
        _form.kullanici_adi = fields.String(_(u"Kullanıcı adınızı giriniz:"))
        _form.ilerle = fields.Button(_(u"Parola Sıfırlama Linki Gönder"))
        self.form_out(_form)

    def bilgi_kontrol(self):
        """
        Girilen kullanıcı adının veritabanında olup olmadığı kontrol edilir.
        Eğer hata yoksa doğrulama linki gönderilir, varsa hata mesajıyla
        birlikte bir önceki adıma gidilip hata mesajı gösterilir ve kullanıcıdan
        kullanıcı adını tekrar girmesi istenir.

        """

        user = User.objects.filter(username=self.input['form']['kullanici_adi'])

        if user:
            self.current.task_data['bilgi_kontrol'] = True
            self.current.task_data['e_posta'] = user[0].e_mail
            self.current.task_data['bilgi'] = user[0].key
        else:
            self.current.task_data['bilgi_kontrol'] = False
            self.current.task_data['msg'] = _(u"Böyle bir kullanıcı bulunmamaktadır. Lütfen tekrar deneyiniz.")
            self.current.task_data['title'] = _(u"Hatalı Bilgi")

    def parola_sifirlama_bilgilendir(self):
        """
        Kullanıcı e_posta adresine gönderilen linke tıklayıp e_posta adresini doğrulamışsa
        kullanıcı, doğrulamanın gerçekleştiği konusunda bilgilendirilir ve yeni parola oluşturma
        ekranına gitmesi istenir.

        """

        _form = JsonForm(current=self.current, title=_(u'Parola Sıfırlama'))
        _form.help_text = _(u"""E-Posta adresiniz başarıyla doğrulanmıştır. Parola
                             oluşturma ekranına giderek yeni parolanızı belirleyebilirsiniz.""")
        _form.parola_olustur = fields.Button(_(u'Parola Oluşturma Ekranına Git'))
        self.form_out(_form)

    def yeni_parola_belirle(self):
        """
        Kullanıcıdan kurallara uygun yeni şifre belirlenmesi istenir. Eğer gösterilecek
        hatalı şifre mesajı varsa gösterilir.

        """

        if self.current.task_data['msg']:
            profil.mesaj_goster(self, _(u'Hatalı Şifre'))
        _form = JsonForm(current=self.current, title=_(u'Yeni Parola Girişi'))
        _form.help_text = _((u"Kendi güvenliğiniz ve sistem güvenliği için yeni oluşturacağınız parola:\n"
                             u"\n"
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

        self.current.task_data['msg'] = profil.yeni_parola_kontrolleri(
            self.input['form']['yeni_parola'],
            self.input['form']['yeni_parola_tekrar'])

    def yeni_parola_kaydet(self):
        """
        Yeni girilen parola kaydedilmeden önce güvenlik nedeniyle
        kurallara uyup uymadığı bir daha kontrol edilir. Eğer uygunsa
        yeni parola kaydedilir. Uygun değilse ki bu beklenmeyen bir
        durumdur. Beklenmeyen hata adımına giderek bu hata mesajı
        kullanıcıya gösterilir.
        """
        self.current.task_data['islem'] = False
        if profil.yeni_parola_kontrolleri(self.input['form']['yeni_parola'],
                                          self.input['form']['yeni_parola_tekrar']) == 'ok':
            kullanici = User.objects.get(self.current.task_data['bilgi'])
            kullanici.set_password(self.input['form']['yeni_parola'])
            kullanici.save()
            Cache(self.current.task_data['kod']).delete()
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
                             İşleme devam edebilmek için belirlediğiniz yeni parolanızla giriş
                             yapmaniz gerekmektedir.""") % (kullanici.name, kullanici.surname)
        _form.giris_yap = fields.Button(_(u"Giriş Ekranına Git"))
        self.form_out(_form)
