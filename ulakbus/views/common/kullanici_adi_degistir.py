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
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster, uygunluk_testi


class KullaniciAdiDegistir(CrudView):
    """
    Kullanıcıların kullanıcı adlarını değiştirebilmelerini sağlar.

    """

    def yeni_kullanici_adi_girisi(self):
        """
        Kullanıcı adı değişikliğini yapabileceği ekran oluşturulur ve yeni kullanıcı adı belirlerken
        hata oluşursa (şu an kullanılan kullanıcı adı bilgisinin yanlış girilmesi gibi), kullanıcıya
        hata mesajı gösterilir.

        """
        if self.current.task_data['msg']:
            mesaj_goster(self, _(u'Kullanıcı Adı Hatalı'))

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

        self.current.task_data['msg'] = kullanici_adi_kontrolu(self, self.input['form']['eski_k_adi'],
                                                               self.input['form']['yeni_k_adi'])

    def yeni_kullanici_adi_kaydet(self):
        """
        Güvenlik açısından kullanıcı adı değişikliği kaydedilmeden önce uygunluk kontrolü
        tekrarlanır. Eğer uygunsa değişiklik yapılır. Uygun değilse ki bu beklenmeyen bir
        durumdur. Beklenmeyen hata adımına gönderilir.

        """
        self.current.task_data['islem'] = False
        if kullanici_adi_kontrolu(self, self.input['form']['eski_k_adi'], self.input['form']['yeni_k_adi']):
            self.current.user.username = self.input['form']['yeni_k_adi']
            self.current.user.save()
            self.current.task_data['islem_mesaji'] = _(u"""'%s' olan kullanıcı adınız
            '%s' olarak değiştirilmiştir.
            Çıkış yapıp yeni kullanıcı adınızla giriş yapabilirsiniz.""") \
                                                     % (
                                                     self.input['form']['eski_k_adi'], self.input['form']['yeni_k_adi'])
            self.current.task_data['islem'] = True
            self.current.task_data['msg'] = None


def kullanici_adi_kontrolu(self, eski_kullanici_adi, yeni_kullanici_adi):
    """
    Kullanıcının şu an kullandığı kullanıcı adı bilgisini doğru girip
    girmediği, şu an kullandığı kullanıcı adı ile yeni belirlediği kullanıcı
    adının aynı olmadığı ve yeni belirlediği kullanıcı adının başka bir kullanıcı
    tarafından alınmadığı kontrol edilir. Eğer kontrollerden geçerse 'ok',
    geçmezse hata mesajı döndürülür.

    Args:
        eski_kullanici_adi (string): Kullanıcının eski kullanıcı adı bilgisi
        yeni_kullanici_adi (string): Kullanıcının yeni kullanıcı adı bilgisi

    Returns:
        (string): 'ok' ya da hata mesajı

    """
    kullanici_adlari = [u.username for u in User.objects.filter()]
    kontrol_listesi = [lambda x: x == self.current.user.username,
                       lambda (x, y): not (x == y), lambda x: not (x in kullanici_adlari)]

    hata_listesi = [_(u'Kullanıcı adınızı yanlış girdiniz. Lütfen tekrar deneyiniz.'),
                    _(u'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır.'),
                    _(u'Böyle bir kullanıcı adı bulunmaktadır. Lütfen başka bir kullanıcı adı deneyiniz.')]

    degiskenler = [eski_kullanici_adi, (eski_kullanici_adi, yeni_kullanici_adi), yeni_kullanici_adi]

    return uygunluk_testi(kontrol_listesi, degiskenler, hata_listesi)
