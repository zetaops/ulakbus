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


class ParolamiUnuttum(CrudView):
    class Meta:
        model = "User"

    def bilgi_girisi(self):

        if self.current.task_data['msg']:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": self.current.task_data['title'],
                "msg": self.current.task_data['msg']}
        else:
            _form = JsonForm(current=self.current, title='Parola Sıfırlama')
            _form.help_text = """Girdiğiniz kullanıcı adınıza kayıtlı birincil e-posta
                                 adresinize parola sıfırlama linki gönderilecektir."""
            _form.kullanici_adi = fields.String("Kullanıcı adınızı giriniz:")
            _form.ilerle = fields.Button("Parola Sıfırlama Linki Gönder")
            self.form_out(_form)

    def parola_sifirlama_bilgilendir(self):

        _form = JsonForm(current=self.current, title='Parola Sıfırlama')
        _form.help_text = """E-Posta adresiniz başarıyla doğrulanmıştır. Parola
                            oluşturma ekranına giderek yeni parolanızı belirleyebilirsiniz."""
        _form.but = fields.Button('Parola Oluşturma Ekranına Git', flow='yeni_parola_belirle')
        self.form_out(_form)

    def bilgi_kontrol(self):

        user = User.objects.filter(username=self.input['form']['kullanici_adi'])

        if user:
            self.current.task_data['bilgi_kontrol'] = True
            self.current.task_data['e_posta'] = user[0].e_mail
            self.current.task_data['bilgi'] = user[0].key
        else:
            self.current.task_data['bilgi_kontrol'] = False

    def hatali_bilgi_uyarisi(self):
        _form = JsonForm(current=self.current, title="Hatalı Bilgi")
        _form.help_text = """Girdiğiniz bilgiler hatalıdır. Lütfen kontrol edip tekrar
                             deneyiniz."""
        _form.geri_don = fields.Button("Geri Dön", flow='bilgi_girisi')
        _form.iptal = fields.Button("İptal")
        self.form_out(_form)

    def yeni_parola_belirle(self):
        _form = JsonForm(current=self.current, title='Yeni Parola Girişi')
        _form.yeni_parola = fields.String("Yeni parolanızı giriniz.")
        _form.yeni_parola_tekrar = fields.String("Yeni parolanızı tekrar giriniz.")
        _form.onayla = fields.Button("Onayla")
        self.form_out(_form)

    def yeni_parola_kaydet(self):
        kullanici = User.objects.get(self.current.task_data['bilgi'])
        kullanici.set_password(self.input['form']['yeni_parola'])
        kullanici.save()
        Cache(self.current.task_data['kod']).delete()

    def parola_degisikligi_bilgilendir(self):
        kullanici = User.objects.get(self.current.task_data['bilgi'])
        _form = JsonForm(current=self.current, title='İşlem Bilgilendirme')
        _form.help_text = """Sayın %s %s, parola sıfırlama işleminiz başarıyla gerçekleştirilmiştir.
                             İşleme devam edebilmek için çıkış yapmanız gerekmektedir. Çıkış
                             yaptıktan sonra belirlediğiniz yeni parolanızla giriş yapabilirsiniz.
                 """ % (kullanici.name, kullanici.surname)
        _form.cikis_yap = fields.Button("Çıkış Yap")
        self.form_out(_form)
