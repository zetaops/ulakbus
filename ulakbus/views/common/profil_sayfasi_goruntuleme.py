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
from ulakbus.lib.common import EPostaDogrulama
from zengine.lib import translation
import re
from zengine.lib.translation import gettext as _, gettext_lazy as __

aktivasyon_kalibi = re.compile('dogrulama=[a-z0-9]{40}')


class KullaniciForm(JsonForm):
    class Meta:
        exclude = ['password', 'superuser', 'harici_okutman', 'ogrenci', 'personel',
                   'last_login_role_key']


class EPostaForm(JsonForm):
    birincil_e_posta = fields.String(__(u"Birincil e-postanız"))


class ProfilGoruntule(UlakbusView):
    """
    Kullanıcıların profil sayfalarını görüntüleyebilmelerini,
    kullanıcı adı, şifre, e-posta, dil seçeneği gibi değişiklikleri
    yapabilmelerini sağlar.

    """

    class Meta:
        model = "User"

    def linkle_gelinmesi_kontrolu(self):
        """
        İş akışının doğrulama linkiyle mi yoksa menüden mi başlatıldığı
        kontrol edilir. Gönderilen doğrulama linki 'dogrulama=4jnjlam90a..'
        şeklindedir. Bu yapıya uyup uymadığı kontrol edilir. İlk try a
        girmez ise linkle gelmemiştir iş akışı menüden başlatılmıştır.

        """
        self.current.task_data['msg'] = None
        self.current.task_data['wf_name'] = self.current.workflow.name
        dogrulama = self.current.input.get('model', '')
        self.current.task_data['link'] = bool(re.match(aktivasyon_kalibi, dogrulama))

    def link_gecerliligi_kontrolu(self):
        """

        Eğer linkle başlatıldıysa, doğrulama linkinin
        geçerli olup olmadığı kontrol edilir.

        """
        self.current.task_data['kod'] = aktivasyon_kodu = self.current.input['model'].split('=')[1]
        self.current.task_data['e_posta'] = EPostaDogrulama(aktivasyon_kodu).get()

    def gecersiz_link_mesaji(self):
        """
        Bağlantı linki geçersiz olmuşsa, uyarı mesajı oluşturulur.

        """
        self.current.task_data['msg'] = _(u"""E-Postanızı onaylamanız için
            gönderilen link geçersiz olmuştur. Lütfen tekrar deneyiniz.""")
        self.current.task_data['title'] = _(u'Geçersiz İşlem')
        self.current.task_data['type'] = 'warning'

    def e_posta_degistir(self):
        """
        E_posta adresi doğrulanmışsa, e_posta değiştirme işlemi yapılır,
        değiştirilecek e_posta bilgisi Cache'den alınır, işlem yapıldıktan sonra
        Cache'den silinir.

        """

        kullanici = User.objects.get(self.current.user_id)
        kullanici.e_mail = self.current.task_data['e_posta']
        kullanici.save()
        EPostaDogrulama(self.current.task_data['kod']).delete()
        self.current.task_data['title'] = _(u'E-Posta Değişikliği')
        self.current.task_data['msg'] = _(
            u'E-Posta değiştirme işleminiz başarıyla gerçekleştirilmiştir.')
        self.current.task_data['type'] = 'info'

    def profil_sayfasi_goruntule(self):
        """
        Profil sayfasının ana görüntülenme ekranını oluşturur, eğer geçersiz link uyarısı,
        başarılı işlem, hatalı işlem gibi görüntülenecek mesaj varsa burada gösterilir.

        """
        if self.current.task_data.get('msg', None):
            self.mesaj_kutusu_goster(self.current.task_data['title'], self.current.task_data['type'])

        u = User.objects.get(self.current.user_id)
        _form = KullaniciForm(u, current=self.current,
                              title=_(u'%s %s Profil Sayfası') % (u.name, u.surname))
        _form.sifre_degistir = fields.Button(_(u"Parola Değiştir"), flow="parola_degistir")
        _form.k_adi_degistir = fields.Button(_(u"Kullanıcı Adı Değiştir"),
                                             flow="kullanici_adi_degistir")
        _form.e_posta_degistir = fields.Button(_(u"E-Posta Değiştir"), flow="e_posta_degistir")
        _form.kaydet = fields.Button(_(u"Kaydet"), flow="kaydet")
        self.form_out(_form)

    def degisiklik_sonrasi_islem(self):
        """
        Kullanıcı adı veya parola değişikliğinden sonra kullanıcıya iki seçenek sunulur.
        Çıkış yapması ya da çıkış yapmadan devam etmesi, bunu seçebileceği ekran gösterilir.

        """
        self.current.task_data['msg'] = _(u"""%s ya da çıkış yapmadan devam edebilirsiniz.
                            Eğer eski bilgilerinizin bilindiği şüphesine sahipseniz 'Çıkış Yap'
                            seçeneğini seçmenizi öneririz.""") % self.current.task_data[
            'islem_mesaji']
        self.mesaj_kutusu_goster('İşlem Bilgilendirme', 'info')

        _form = JsonForm(current=self.current, title=_(u"İşlem Seçeneği"))
        _form.cikis = fields.Button(_(u"Çıkış Yap"), flow='cikis_yap')
        _form.devam = fields.Button(_(u"Çıkış Yapmadan Devam Et"))
        self.form_out(_form)

    def dil_sayi_zaman_ayarlari_degistir(self):
        """
        Profil sayfasında dil seçenekleri, sayı ve zaman formatları kullanıcı tarafından
        değiştirilebilir. Bu değişiklikler kaydedilir ve bu bilgiler session da tutulduğu için
        session bilgisi sıfırlanır. Session'da bulamadığında bu bilgileri bir kereye mahsus
        olmak üzere modelden değişmiş halini alır ve en son halini sessiona koyar.

        """

        kullanici = self.current.user

        for k in translation.DEFAULT_PREFS.keys():
            self.current.session[k] = ''
            setattr(kullanici, k, self.input['form'][k])
        kullanici.blocking_save()
        self.current.output['cmd'] = 'reload'
        self.current.output['title'] = _(u'Dil, Sayı, Zaman Formatı Değişikliği')
        self.current.output['msg'] = _(u'Değişiklikleriniz başarıyla kaydedilmiştir. Ana sayfaya yönlendiriliyorsunuz.')