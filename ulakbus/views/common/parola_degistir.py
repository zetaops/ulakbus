# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import fields
import re
from zengine.lib.translation import gettext as _
from ulakbus.views.common.profil_sayfasi_goruntuleme import mesaj_goster, uygunluk_testi

ozel_karakterler = '*&^%$@!?.:/><; '
ozel_karakter = re.compile("[%s]" % ozel_karakterler)


class ParolaDegistir(CrudView):
    """
    Kullanıcıların parolalarını değiştirebilmelerini sağlar.
    """

    def yeni_parola_girisi(self):
        """
        Parola değişikliği ekranını oluşturur, kullanıcı parolasını değiştirirken hata yaparsa
        (8 karakterden az parola seçimi gibi), hata kontrol edildikten sonra yine bu ekranda
        gösterilir.

        """

        if self.current.task_data['msg']:
            mesaj_goster(self, _(u'Parola Hatalı'))

        _form = JsonForm(current=self.current, title=_(u'Parola Değiştirme'))
        _form.help_text = _((u"Kendi güvenliğiniz ve sistem güvenliği için yeni oluşturacağınız parola:\n"
                             u"\n"
                             u"* 8 karakterden büyük olmalı,\n"
                             u"* En az bir küçük harf, bir büyük harf, bir sayı ve bir özel karakter içermeli,\n"
                             u"* Eski şifrenizle aynı olmamalıdır.\n"
                             u"* Özel karakterler = [\* & ^ % $ @ ! ? . : / > < ; ]\n"
                             u"* Örnek parola = Ulakbüs3\*\n"))

        _form.eski_parola = fields.String(_(u"Şu an kullandığınız parolanızı giriniz."))
        _form.yeni_parola = fields.String(_(u"Yeni parolanızı giriniz."))
        _form.yeni_parola_tekrar = fields.String(_(u"Yeni parolanızı tekrar giriniz."))
        _form.degistir = fields.Button(_(u"Parola Değiştir"))
        self.form_out(_form)

    def yeni_parola_kontrol(self):
        """
        Girilen parolalar önce Cache'e atılır. Ardından parola kontrol methodlarına gönderilir.
        Eğer parola kontrol methodlarından geçerse parola kaydetme adımına gidilir. Eğer parola
        değişikliğinde bir hata olursa hata mesajı ile bir önceki adıma gidilip, hata gösterilir
        ve parola değişikliğini yeniden denemesi istenir.

        """
        self.current.task_data['msg'] = eski_parola_kontrolleri(self, self.input['form']['eski_parola'],
                                                                self.input['form']['yeni_parola'],
                                                                self.input['form']['yeni_parola_tekrar'])

        if self.current.task_data['msg'] == 'ok':
            self.current.task_data['msg'] = yeni_parola_kontrolleri(
                self.input['form']['yeni_parola'],
                self.input['form']['yeni_parola_tekrar'])

    def yeni_parola_kaydet(self):
        """
        Cache'e atılan parolalar güvenlik nedeniyle tekrardan parola kontrol methodlarına
        gönderilir. Kontrolden geçerse parola değiştirilir ve işlem başarılı mesajı yaratılır.
        Eğer kontrolden geçmezse ki bu beklenmeyen bir durumdur. Beklenmeyen hata adımına gidilir
        ve hata gösterilir.

        """
        eski_parola = self.input['form']['eski_parola']
        yeni_parola = self.input['form']['yeni_parola']
        yeni_parola_tekrar = self.input['form']['yeni_parola_tekrar']
        self.current.task_data['islem'] = False
        if eski_parola_kontrolleri(self, eski_parola, yeni_parola, yeni_parola_tekrar) == \
                yeni_parola_kontrolleri(yeni_parola, yeni_parola_tekrar) == 'ok':
            self.current.user.set_password(yeni_parola)
            self.current.user.save()
            self.current.task_data['islem'] = True
            self.current.task_data['msg'] = None
            self.current.task_data['islem_mesaji'] = _(u"""Parolanız başarıyla değiştirildi. Çıkış
                                                     yapıp yeni parolanızla giriş yapabilirsiniz""")


def eski_parola_kontrolleri(self, eski_parola, yeni_parola, yeni_parola_tekrar):
    """
    Kullanıcının eski parolasının doğruluğu, yeni parola ile yeni parola tekrarı
    bilgisinin aynı olduğu ve eski parolanın yeni parola ile aynı olmadığı kontrol
    edilir. Eğer kontrollerden geçerse 'ok', geçmezse hata mesajı döndürülür.

    Args:
        eski_parola (string): kullanıcının eski parola bilgisi
        yeni_parola (string): kullanıcının yeni parola bilgisi
        yeni_parola_tekrar (string): kullanıcının yeni parola tekrarının bilgisi

    Returns:
        (string): 'ok' ya da hata mesajı

    """

    kontrol_listesi = [lambda x: self.current.user.check_password(x),
                       lambda (x, y): x == y, lambda (x, y, z): not (x == y == z)]

    hata_listesi = [_(u'Kullanmakta olduğunuz parolanızı yanlış girdiniz.'),
                    _(u'Yeni parolanız ve tekrarı uyuşmamaktadır.'),
                    _(u'Yeni parolanız ile eski parolanız aynı olmamalıdır.')]

    degiskenler = [eski_parola, (yeni_parola, yeni_parola_tekrar),
                   (eski_parola, yeni_parola, yeni_parola_tekrar)]

    return uygunluk_testi(kontrol_listesi, degiskenler, hata_listesi)


def yeni_parola_kontrolleri(yeni_parola, yeni_parola_tekrar):
    """
    Kullanıcının yeni parola ile yeni parola tekrarı bilgisinin aynı olduğu,
    yeni parolanın en az 8 en fazla 100 karakterden oluştuğu, en az bir tane
    büyük harf, küçük harf, sayı ve özel karakter içerdiği kontrol edilir.
    Eğer kontrollerden geçerse 'ok', geçmezse hata mesajı döndürülür.

    Args:
        yeni_parola (string): kullanıcının yeni parola bilgisi
        yeni_parola_tekrar (string): kullanıcının yeni parola tekrarının bilgisi

    Returns:
         (string): 'ok' ya da hata mesajı

    """

    kontrol_listesi = [lambda (x, y): x == y, lambda x: 8 <= len(x) <= 100,
                       lambda x: ozel_karakter.search(x)]

    hata_listesi = [_(u'Yeni parolanız ve tekrarı uyuşmamaktadır.'),
                    _(u'Yeni parolanız en az 8 karakterden oluşmalıdır.'),
                    _(u'Yeni parolanız en az bir tane özel karakter içermelidir: [%s]')
                    % ' '.join(ozel_karakterler)]

    degiskenler = [(yeni_parola, yeni_parola_tekrar), yeni_parola, yeni_parola]

    msg = uygunluk_testi(kontrol_listesi, degiskenler, hata_listesi)

    if msg == 'ok':
        msg = kucuk_buyuk_sayi_kontrolu(yeni_parola)

    return msg


def kucuk_buyuk_sayi_kontrolu(parola):
    """
    Verilen bir parola string i içinde en az bir tane büyük harf,
    küçük harf ve sayı bulunup bulunmadığını kontrol eder. Eğer hepsi
    kontrolden geçerse 'ok' geçmezse hata mesajı döndürülür.

    Args:
        parola (string): Kullanıcının yeni olarak belirlemek istediği parola.

    Returns:
         (string): 'ok' ya da hata mesajı

    """
    msg = 'ok'
    kontrol_listesi = ['isupper', 'islower', 'isdigit']

    for karakter in parola:
        for fonksiyon in kontrol_listesi:
            if getattr(karakter, fonksiyon)():
                kontrol_listesi.remove(fonksiyon)

    if kontrol_listesi:
        msg = _(
            u'Yeni parolanız en az bir küçük harf, bir büyük harf ve bir sayı içermelidir. Örnek parola = Ulakbüs2*')

    return msg
