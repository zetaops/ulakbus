# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms import   fields
from ulakbus.models import User
import random
import datetime
import hashlib
from zengine.lib.cache import Cache
from ulakbus.services.zato_wrapper import E_PostaYolla

class KullaniciForm(JsonForm):
    class Meta:
        exclude = ['password', 'superuser', 'harici_okutman', 'ogrenci', 'personel']

class EPostaForm(JsonForm):
    birincil_e_posta = fields.String("Birincil e-postanız")


class ProfilGoruntule(CrudView):
    """
    CrudView üzerine geliştirilmiştir.

    İş akışının tek adımına karşılık gelen tek bir metoda sahiptir.

    """

    class Meta:
        model = "User"

    def profil_sayfasi_islem_secenegi(self):
        self.current.task_data['islem_secenek'] = False
        try:
            # Bir linkle giriş yapılmaya çalışıldığını gösterir.
            aktivasyon_kodu = self.current.input['model'].split('=')[1]

            # Linkin geçerliliğini kaybedip kaybetmediği test edilir.
            if Cache(aktivasyon_kodu).get():

                self.current.task_data['islem_secenek'] = True
                self.current.task_data['kod'] = aktivasyon_kodu
                self.current.task_data['bilgi'] = Cache(aktivasyon_kodu).get()

            else:
                # Link geçersizse
                self.current.task_data['msg'] = """E-Postanızı onaylamanız için gönderilen link geçersiz olmuştur.
                                                       Lütfen tekrar deneyiniz."""
                self.current.task_data['title'] = 'Geçersiz İşlem'
                self.current.task_data['type'] = 'warning'

        except KeyError:
            # Linkle tıklanarak değil, iş akışı menüden başlatılmışsa
            self.current.task_data['msg'] = None

    def e_posta_degistir(self):

        u = User.objects.get(self.current.user_id)
        u.e_mail = self.current.task_data['bilgi']
        u.save()
        Cache(self.current.task_data['kod']).delete()

        self.current.task_data['msg'] = 'E-Posta değiştirme işleminiz başarıyla gerçekleştirilmiştir.'
        self.current.task_data['title'] = 'E-Posta Değişikliği'
        self.current.task_data['type'] = 'info'

    def profil_sayfasi_goruntule(self):

        if self.current.task_data['msg']:
            self.current.output['msgbox'] = {
            'type': self.current.task_data['type'], "title": self.current.task_data['title'],
            "msg": self.current.task_data['msg']}

        u = User.objects.get(self.current.user_id)
        _form = KullaniciForm(u, current=self.current, title='%s %s Profil Sayfası' % (u.name, u.surname))
        _form.sifre_degistir = fields.Button("Şifre Değiştir", flow="yeni_sifre_girisi")
        _form.k_adi_degistir = fields.Button("Kullanıcı Adı Değiştir", flow="yeni_kullanici_adi_girisi")
        _form.e_posta_degistir = fields.Button("E-Posta Değiştir", flow="varolan_e_posta_sec")
        _form.kaydet = fields.Button("Kaydet", flow="kaydet")
        self.form_out(_form)

    def yeni_sifre_girisi(self):

        _form = JsonForm(current=self.current, title='Şifre Değiştirme')
        _form.eski_sifre = fields.String("Şu an kullandığınız şifrenizi giriniz.")
        _form.yeni_sifre = fields.String("Yeni şifrenizi giriniz.")
        _form.yeni_sifre_tekrar = fields.String("Yeni şifrenizi tekrar giriniz.")
        _form.degistir = fields.Button("Şifre Değiştir")
        self.form_out(_form)

        # Burada şu an kullanılan olarak girilen şifrenin doğruluğu ve yeni girilen
        # şifre ile yeni şifrenin tekrarının uyuştuğu kontrol edilmelidir.

    def yeni_sifre_kaydet(self):
        if self.current.user.check_password(self.input['form']['eski_sifre']) and \
                        self.input['form']['yeni_sifre'] == self.input['form']['yeni_sifre_tekrar']:
            self.current.user.set_password(self.input['form']['yeni_sifre'])
            self.current.user.save()

        self.current.task_data['islem_mesaji'] = """Şifreniz başarıyla değiştirildi.
                                    Çıkış yapıp yeni şifrenizle giriş yapabilirsiniz"""

        # Eski şifre ile yeni şifrenin aynı olmaması kontrol edilmeli mi?
        # Belli bir karakter sınırı koyulmalı mı?

    def degisiklik_sonrasi_islem(self):
        _form = JsonForm(current=self.current, title="İşlem Bilgilendirme")
        _form.help_text = """%s ya da çıkış yapmadan devam edebilirsiniz.
                            Eğer eski bilgilerinizin bilindiği şüphesine sahipseniz 'Çıkış Yap'
                            seçeneğini seçmenizi öneririz.""" % self.current.task_data['islem_mesaji']
        _form.cikis = fields.Button("Çıkış Yap")
        _form.devam = fields.Button("Çıkış Yapmadan Devam Et", flow='profil_sayfasi_islem_secenegi')
        self.form_out(_form)

    def yeni_kullanici_adi_girisi(self):
        _form = JsonForm(current=self.current, title='Kullanıcı Adı Değiştirme')
        _form.eski_k_adi = fields.String("Şu an kullandığınız kullanıcı adınızı giriniz.")
        _form.yeni_k_adi = fields.String("Yeni kullanıcı adınızı giriniz.")
        _form.degistir = fields.Button("Kullanıcı Adı Değiştir")
        self.form_out(_form)

        # Şu an kullanılan kullanıcı adının doğruluğu, eskisi ile yeni kullanıcı
        # adının aynı olmaması ve yeni kullanıcı adının kullanılmıyor olması burda
        # kontrol edilmelidir.

    def yeni_kullanici_adi_kaydet(self):
        kullanici_adlari = [u.username for u in User.objects.filter()]
        if self.current.user.username == self.input['form']['eski_k_adi'] and\
                        self.input['form']['eski_k_adi']!=self.input['form']['yeni_k_adi'] and\
                        self.input['form']['yeni_k_adi'] not in kullanici_adlari:
            self.current.user.username = self.input['form']['yeni_k_adi']
            self.current.user.save()

            self.current.task_data['islem_mesaji'] = """%s olan kullanıcı adınız %s
             olarak değiştirilmiştir. Çıkış yapıp yeni kullanıcı adınızla giriş
             yapabilirsiniz"""      %  (self.input['form']['eski_k_adi'],
                                        self.input['form']['yeni_k_adi'])

    def yeni_e_posta_girisi(self):
        _form = EPostaForm(current=self.current, title='Yeni E-Posta Girişi')
        _form.birincil_e_posta = self.current.user.e_mail
        _form.e_posta = fields.String("Birincil olarak belirlemek istediğiniz e-posta adresinizi yazınız.")
        _form.degistir = fields.Button("Doğrulama Linki Yolla")
        self.form_out(_form)

    def aktivasyon_maili_yolla(self):

        try:
            self.current.task_data["bilgi"] = self.current.task_data["e_posta"] = self.input['form']['e_posta']
        except KeyError:
            pass

        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()

        try:
            posta_gonder = E_PostaYolla(service_payload={"wf_name": self.current.workflow_name,
                                               "e_posta": self.current.task_data["e_posta"],
                                               "aktivasyon_kodu": self.current.task_data["aktivasyon"],
                                               "bilgi":self.current.task_data["bilgi"]})
            posta_gonder.zato_request()

        except ValueError:
            pass

    def link_gonderimi_bilgilendir(self):
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'E-Posta Doğrulama',
            "msg": """%s adresinize doğrulama linki gönderilmiştir. Lütfen e-posta'nızdaki bağlantı linkine
             tıklayarak mailin size ait olduğunu doğrulayınız. """ % (self.current.task_data['e_posta'])
        }

    def kaydet(self):
        self.set_form_data_to_object()
        self.object.blocking_save()
        self.current.task_data['msg'] = 'Değişiklikleriniz başarıyla kaydedilmiştir.'
        self.current.task_data['title'] = 'Bilgilendirme Mesajı'

def aktivasyon_kodu_uret():
    rand = "%s%s%s" % (str(random.randrange(100000000000)), str(datetime.datetime.now()),
                       str(random.randrange(100000000000)))

    hash_object = hashlib.sha1(rand)
    hex_dig = hash_object.hexdigest()

    return hex_dig


