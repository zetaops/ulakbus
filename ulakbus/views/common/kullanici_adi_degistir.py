# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from ulakbus.lib.views import UlakbusView
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.lib.translation import gettext as _
from ulakbus.lib.common import kullanici_adi_kontrolleri


class KullaniciAdiDegistir(UlakbusView):
    """
    Kullanıcıların kullanıcı adlarını değiştirebilmelerini sağlar.

    """

    def yeni_kullanici_adi_girisi(self):
        """
        Kullanıcı adı değişikliğini yapabileceği ekran oluşturulur ve yeni kullanıcı adı belirlerken
        hata oluşursa (şu an kullanılan kullanıcı adı bilgisinin yanlış girilmesi gibi), kullanıcıya
        hata mesajı gösterilir.

        """
        self.current.task_data['deneme_sayisi'] = 3
        if self.current.task_data.get('msg', None):
            self.mesaj_kutusu_goster(_(u'Kullanıcı Adı Hatalı'))

        _form = JsonForm(current=self.current, title=_(u'Kullanıcı Adı Değiştirme'))
        _form.eski_k_adi = fields.String(_(u"Şu an kullandığınız kullanıcı adınızı giriniz."))
        _form.yeni_k_adi = fields.String(_(u"Yeni kullanıcı adınızı giriniz."))
        _form.degistir = fields.Button(_(u"Kullanıcı Adı Değiştir"))
        self.form_out(_form)

    def yeni_kullanici_adi_kontrol(self):
        """
        Kullanıcı adı değiştirilirken kurallara uyulup uyulmadığı kontrol edilir, uygunsa kaydetme
        ekranına, uyulmamışsa hata mesajıyla birlikte bir önceki adıma gönderilir.

        """
        kullanici_adi = self.current.user.username
        self.current.task_data['eski_k_adi'] = self.input['form']['eski_k_adi']
        self.current.task_data['yeni_k_adi'] = self.input['form']['yeni_k_adi']

        self.current.task_data['uygunluk'], self.current.task_data['msg'] = \
            kullanici_adi_kontrolleri(self.current.task_data['eski_k_adi'],
                                      self.current.task_data['yeni_k_adi'], kullanici_adi)

    def islem_onayi_icin_parola_girisi(self):
        """
        Kullanıcının parolasını girdiği form oluşturulur.

        """

        if self.current.task_data['msg']:
            self.mesaj_kutusu_goster(_(u'Hatalı Parola Girişi'))
        _form = JsonForm(current=self.current, title=_(u'İşlem Onayı İçin Parola Doğrulama'))
        _form.parola = fields.String(
            _(u"Bu işlemi gerçekleştirebilmek için güncel parolanızı girmeniz gerekmektedir."),
            type="password")
        _form.dogrula = fields.Button(_(u"Parola Doğrula"))
        self.form_out(_form)

    def parola_kontrol(self):
        """
        Parola kontrol edilir. Doğruysa kullanıcı adı değiştirme ekranına gidilir.
        Yanlış ise deneme hak sayısı bir azaltılarak tekrardan parolasını girmesi
        istenir.

        """

        self.current.task_data['deneme_sayisi'] -= 1
        self.current.task_data['msg'] = _(u'Parolanızı yanlış girdiniz. Lütfen tekrar deneyiniz.')
        self.current.task_data['gecerli_sifre'] = self.current.user.check_password(
            self.current.input['form']['parola'])

    def cikis_mesaji_olustur(self):
        """
        Değişiklik işlemi yapılırken güvenlik açısından kullanıcının parolasını girmesi
        istenir. Üç kez deneme hakkı verilir. Parola üç kez yanlış girildiğinde kullanıcının
        yapmak istediği işlem gerçekleştirilmez ve çıkış yaptırılır.

        """

        self.current.task_data['show_logout_message'] = True
        self.current.task_data['logout_title'] = 'Hatalı Parola Girişi'
        self.current.task_data['logout_message'] = """Parolanızı üst üste üç kez yanlış
                                                girdiğiniz için çıkışa yönlendiriliyorsunuz."""

    def yeni_kullanici_adi_kaydet(self):
        """
        Güvenlik açısından kullanıcı adı değişikliği kaydedilmeden önce uygunluk kontrolü
        tekrarlanır. Eğer uygunsa değişiklik yapılır. Uygun değilse ki bu beklenmeyen bir
        durumdur. Beklenmeyen hata adımına gönderilir.

        """

        self.current.user.username = self.current.task_data['yeni_k_adi']
        self.current.user.save()
        self.current.task_data['islem_mesaji'] = _(u"""'%s' olan kullanıcı adınız
                                                 '%s' olarak değiştirilmiştir.Çıkış yapıp yeni kullanıcı
                                                 adınızla giriş yapabilirsiniz """) \
                                                 % (self.current.task_data['eski_k_adi'],
                                                    self.current.task_data['yeni_k_adi'])
