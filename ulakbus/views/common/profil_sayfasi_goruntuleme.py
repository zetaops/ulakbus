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
import random
import datetime
import hashlib
from zengine.lib.cache import Cache
from ulakbus.services.zato_wrapper import E_PostaYolla
from zengine.lib import translation
import re
from zengine.lib.translation import gettext as _, gettext_lazy as __

rgx = re.compile('dogrulama=[a-z0-9]{40}')
kullanici_adlari = [u.username for u in User.objects.filter()]
ozel_karakterler = '*&^%$@!?.:/><; '
ozel_karakter = re.compile("[%s]" % ozel_karakterler)


class KullaniciForm(JsonForm):
    class Meta:
        exclude = ['password', 'superuser', 'harici_okutman', 'ogrenci', 'personel']


class EPostaForm(JsonForm):
    birincil_e_posta = fields.String(__(u"Birincil e-postanız"))


class ProfilGoruntule(CrudView):
    """
    Kullanıcıların profil sayfalarını görüntüleyebilmelerini,
    kullanıcı adı, şifre, e-posta, dil seçeneği gibi değişiklikleri
    yapabilmelerini sağlar.

    """

    class Meta:
        model = "User"

    def profil_sayfasi_islem_secenegi(self):
        """
        İş akışının doğrulama linkiyle mi yoksa menüden mi başlatıldığı
        kontrol edilir. Eğer linkle başlatıldıysa, doğrulama linkinin
        geçerli olup olmadığı kontrol edilir.

        """
        self.current.task_data['msg'] = None
        self.current.task_data['type'] = 'info'
        self.current.task_data['islem_secenek'] = None

        try:
            # Linkle gelindiğini kontrol eder. Gönderilen doğrulama linki
            # 'dogrulama=4jnjlam90a..' şeklindedir. Bu yapıya uyup uymadığı
            # kontrol edilir. İlk try a girmez ise linkle gelmemiştir iş akışı
            # menüden başlatılmıştır. İkinci if'e girerse linkle gelmiş ve
            # link hala geçerli girmezse link geçersiz olmuş demektir.
            if rgx.search(self.current.input['model']):
                aktivasyon_kodu = self.current.input['model'].split('=')[1]
                self.current.task_data['islem_secenek'] = 'gecersiz_link'

                # Eğer linkle gelinmiş ise, bağlantı linkinin hala geçerli olup
                # olmadığı kontrol edilir.
                if Cache(aktivasyon_kodu).get():
                    self.current.task_data['islem_secenek'] = 'gecerli_link'
                    self.current.task_data['kod'] = aktivasyon_kodu
                    self.current.task_data['bilgi'] = Cache(aktivasyon_kodu).get()
        except KeyError:
            pass

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

        u = User.objects.get(self.current.user_id)
        u.e_mail = self.current.task_data['bilgi']
        u.save()
        Cache(self.current.task_data['kod']).delete()
        self.current.task_data['title'] = _(u'E-Posta Değişikliği')
        self.current.task_data['msg'] = _(u'E-Posta değiştirme işleminiz başarıyla gerçekleştirilmiştir.')

    def profil_sayfasi_goruntule(self):
        """
        Profil sayfasının ana görüntülenme ekranını oluşturur, eğer görüntülenecek mesaj varsa,
        geçersiz link, başarılı işlem, hatalı işlem gibi burada gösterilir.

        """

        if self.current.task_data['msg']:
            mesaj_goster(self, self.current.task_data['title'], self.current.task_data['type'])

        u = User.objects.get(self.current.user_id)
        _form = KullaniciForm(u, current=self.current, title=_(u'%s %s Profil Sayfası') % (u.name, u.surname))
        _form.sifre_degistir = fields.Button(_(u"Parola Değiştir"), flow="yeni_parola_girisi")
        _form.k_adi_degistir = fields.Button(_(u"Kullanıcı Adı Değiştir"), flow="yeni_kullanici_adi_girisi")
        _form.e_posta_degistir = fields.Button(_(u"E-Posta Değiştir"), flow="varolan_e_posta_sec")
        _form.kaydet = fields.Button(_(u"Kaydet"), flow="kaydet")
        self.form_out(_form)

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
            self.current.task_data['islem_mesaji'] = _(u"""Parolanız başarıyla değiştirildi. Çıkış
                                                     yapıp yeni parolanızla giriş yapabilirsiniz""")

    def hata_mesaji_goster(self):
        """
        Eğer parola kaydederken parola kontrolünden geçemezse bu beklenmeyen
        bir durumdur ve beklenmeyen hata mesajı gösterilir.

        """
        self.current.task_data['msg'] = _(u'Beklenmeyen bir hata oluştu, lütfen işleminizi tekrarlayınız.')
        mesaj_goster(self, _(u'Hatalı İşlem'))

    def degisiklik_sonrasi_islem(self):
        """
        Kullanıcı adı veya parola değişikliğinden sonra kullanıcıya iki seçenek sunulur. Çıkış yapması
        ya da çıkış yapmadan devam etmesi, bunu seçebileceği ekran gösterilir.

        """
        _form = JsonForm(current=self.current, title=_(u"İşlem Bilgilendirme"))
        _form.help_text = _(u"""%s ya da çıkış yapmadan devam edebilirsiniz.
                            Eğer eski bilgilerinizin bilindiği şüphesine sahipseniz 'Çıkış Yap'
                            seçeneğini seçmenizi öneririz.""") % self.current.task_data['islem_mesaji']
        _form.cikis = fields.Button(_(u"Çıkış Yap"))
        _form.devam = fields.Button(_(u"Çıkış Yapmadan Devam Et"), flow='profil_sayfasi_islem_secenegi')
        self.form_out(_form)

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
            % (self.input['form']['eski_k_adi'], self.input['form']['yeni_k_adi'])
            self.current.task_data['islem'] = True

    def yeni_e_posta_girisi(self):
        """
        Kullanıcının birincil e_posta değişikliğini yapabileceği ekran oluşturulur ve birincil olarak belirlemek
        istediği e_posta adresini girmesi istenir. Bu işlem sonunda girdiği adrese doğrulama linki gönderilecektir.

        """
        _form = EPostaForm(current=self.current, title=_(u'Yeni E-Posta Girişi'))
        _form.help_text = _(u"""Birincil olarak belirlemek istediğiniz e-posta adresinize
                          doğrulama linki gönderilecektir.""")
        _form.birincil_e_posta = self.current.user.e_mail
        _form.e_posta = fields.String(_(u"Birincil olarak belirlemek istediğiniz e-posta adresinizi yazınız."))
        _form.degistir = fields.Button(_(u"Doğrulama Linki Yolla"))
        self.form_out(_form)

    def e_posta_bilgisini_kaydet(self):
        """
        Doğrulama linki gönderilecek e_posta adresi cache'e kaydedilir.

        """

        self.current.task_data["bilgi"] = self.current.task_data["e_posta"] = self.input['form']['e_posta']

    def aktivasyon_maili_yolla(self):
        """
        Hashlenmiş 40 karakterli bir aktivasyon kodu üretilir ve cache'e atılır. Zato servisi ile
        kullanıcının yeni olarak belirlediği e_posta adresine doğrulama linki gönderilir.

        """

        self.current.task_data["aktivasyon"] = aktivasyon_kodu_uret()

        posta_gonder = E_PostaYolla(service_payload={
            "wf_name": self.current.workflow_name,
            "e_posta": self.current.task_data["e_posta"],
            "aktivasyon_kodu": self.current.task_data["aktivasyon"],
            "bilgi": self.current.task_data["bilgi"]})

        posta_gonder.zato_request()

    def link_gonderimi_bilgilendir(self):
        """
        Doğrulama linki yollandığında kullanıcı linkin yollandığına dair bilgilendirilir.

        """
        self.current.task_data['msg'] = _(u"""'%s' adresinize doğrulama linki gönderilmiştir.
        Lütfen e-posta'nızdaki bağlantı linkine tıklayarak e-posta adresinin size ait
        olduğunu doğrulayınız. """) % (self.current.task_data['e_posta'])

        mesaj_goster(self, 'E-Posta Doğrulama', 'info')

    def kaydet(self):
        """
        Profil sayfasında dil seçenekleri, sayı ve zaman formatları kullanıcı tarafından
        değiştirilebilir. Bu değişiklikler kaydedilir ve bu bilgiler session da tutulduğu için
        session bilgisi sıfırlanır. Session'da bulamadığında bu bilgileri bir kereye mahsus
        olmak üzere modelden değişmiş halini alır ve en son halini sessiona koyar.

        """
        self.set_form_data_to_object()
        self.object.blocking_save()
        self.current.task_data['msg'] = _(u'Değişiklikleriniz başarıyla kaydedilmiştir.')
        self.current.task_data['title'] = _(u'Bilgilendirme Mesajı')
        self.current.task_data['type'] = 'info'

        for k in translation.DEFAULT_PREFS.keys():
            self.current.session[k] = ''


def aktivasyon_kodu_uret():
    """
    Unique olması açısından iki tane 12 karakterli random sayı ile anlık zaman bilgisinin
    birleşiminden rastgele bir string oluşturulur. Bu string sha1 ile hashlenir ve 40
    karakterli bir aktivasyon kodu üretilir.

    """
    rastgele_sayi = "%s%s%s" % (str(random.randrange(100000000000)),
                                str(datetime.datetime.now()),
                                str(random.randrange(100000000000)))

    hash_objesi = hashlib.sha1(rastgele_sayi)
    aktivasyon_kodu = hash_objesi.hexdigest()

    return aktivasyon_kodu


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
    kontrol_listesi = [lambda x: x == self.current.user.username,
                       lambda (x, y): not (x == y), lambda x: not (x in kullanici_adlari)]

    hata_listesi = [_(u'Kullanıcı adınızı yanlış girdiniz. Lütfen tekrar deneyiniz.'),
                    _(u'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır.'),
                    _(u'Böyle bir kullanıcı adı bulunmaktadır. Lütfen değiştirerek tekrar deneyiniz.')]

    degiskenler = [eski_kullanici_adi, (eski_kullanici_adi, yeni_kullanici_adi), yeni_kullanici_adi]

    return uygunluk_testi(kontrol_listesi, degiskenler, hata_listesi)


def uygunluk_testi(kontrol_listesi, degiskenler, hata_listesi):
    """
    Kontrol listesi verilen değişkenler ile sırayla kontrol edilir,
    eğer bir hata ile karşılaşılırsa döngüden çıkılır ve hata mesajı
    döndürülür. Eğer hepsi kontrolden geçerse 'ok' mesajı döndürülür.

    Args:
        kontrol_listesi (list): lambda methodlarının bulunduğu bir liste
        degiskenler (list): methodları çalıştırmak için gerekli olan
                            değişkenlerin bulunduğu liste
        hata_listesi (list): her bir methodun çalışmaması halinde karşılık
                             gelen hata mesajlarından oluşan liste

    Returns:
         (string): 'ok' ya da hata mesajı

    """
    msg = 'ok'
    for i, fonksiyon in enumerate(kontrol_listesi):
        if not fonksiyon(degiskenler[i]):
            msg = hata_listesi[i]
            break

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

def mesaj_goster(self, title, type='warning'):
    """
    Hatalı işlem, başarılı işlem gibi bir çok yerde kullanılan mesaj kutularını
    her defasında tanımlamak yerine bu method yardımıyla kullanılmasını sağlar.

    Args:
        title (string): Mesaj kutusunun başlığı
        type (string): Mesaj kutusunun tipi (warning, info)

    """
    self.current.output['msgbox'] = {
        'type': type, "title": title,
        "msg": self.current.task_data['msg']}
    self.current.task_data['msg'] = None

