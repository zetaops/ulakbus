# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from zengine.lib import translation
import random
from ulakbus.lib.common import EPostaDogrulama

k_adi_parametreleri = ['eski_k_adi', 'yeni_k_adi']
k_adi_hatalari = [('yanlis_k_adi', 'yanlis_k_adi', 'Kullanıcı adınızı yanlış girdiniz'),
                  ('ulakbus', 'ulakbus',
                   'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır'),
                  ('ulakbus', 'personel_isleri_1', 'Böyle bir kullanıcı adı bulunmaktadır')]

parola_parametreleri = ['eski_parola', 'yeni_parola', 'yeni_parola_tekrar']
parola_hatalari = [
    ('parola', 'parola', 'parola', 'Kullanmakta olduğunuz parolanızı yanlış girdiniz.'),
    ('123', 'paro', 'parola', 'Yeni parolanız ve tekrarı uyuşmamaktadır.'),
    ('123', '123', '123', 'Yeni parolanız ile eski parolanız aynı olmamalıdır.'),
    ('123', 'paro', 'paro', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'parolapar', 'parolapar', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'PAROLAPAR', 'PAROLAPAR', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'PaRoLaPaR', 'PaRoLaPaR', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'parola33', 'parola33', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'PAROLA33', 'PAROLA33', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'parola**', 'parola**', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'PAROLA**', 'PAROLA**', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', '*#&&*$%^&()', '*#&&*$%^&()', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', '123456789', '123456789', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'PaRoLaPaR', 'PaRoLaPaR', 'Girmiş olduğunuz parola kurallara uymamaktadır.'),
    ('123', 'yanliŞ*par3', 'yanliŞ*par3', 'Girmiş olduğunuz parola kurallara uymamaktadır.')]


class TestCase(BaseTestCase):
    user_key = 'iG4mvjQrfkvTDvM6Jk56X5ILoJ'
    user = User.objects.get(user_key)
    user.e_mail = 'ulakbus_deneme_birincil_maili@ulakbus.com'
    user.username = 'ulakbus'
    user.password = '123'
    user.save()

    def test_profil_sayfasi(self):

        # Test edilecek iş akışı seçilir.
        # ulakbus kullanıcısıyla giriş yapılır.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        resp = self.client.post()
        # Linkle gelinmenin olmadığı test edilir.
        assert self.client.current.task_data['link'] == False
        # Profil sayfasının görüntülenmesi test edilir.
        assert 'Profil Sayfası' in resp.json['forms']['schema']["title"]

    def test_dil_sayi_zaman_ayarlari_degistir(self):
        # Dil, sayı ve zaman seçenekleri alınır.
        diller = translation.available_translations.keys()
        zamanlar = translation.available_datetimes.keys()
        sayilar = translation.available_numbers.keys()
        # Bu alınan seçeneklerden rastgele bir tane seçilerek bir sözlük içerisine koyulur.
        ornek_degerler = {}
        ornek_degerler['locale_language'] = random.choice(diller)
        ornek_degerler['locale_datetime'] = random.choice(zamanlar)
        ornek_degerler['locale_number'] = random.choice(sayilar)
        # Rastgele seçilen bu değerler seçilir ve kaydet butonuna basılır.
        # Seçilen değerin kaydedilip ekranda gösterilmesi test edilir.
        # Kaydetme işleminden sonra mesaj kutusunun çıkması ve bu mesaj
        # kutusunun başlığının 'Bilgilendirme Mesajı' olması test edilir.
        for k, v in ornek_degerler.items():
            resp = self.client.post(form={k: v}, flow="kaydet")
            assert resp.json["msgbox"]["title"] == "Bilgilendirme Mesajı"
            assert resp.json["forms"]["model"][k] == v

    def test_parola_degistir_basarisiz(self):
        # Parola değiştirme iş akışına geçiş yapılır.
        resp = self.client.post(flow="parola_degistir")
        # Parola değiştirme ekranındaki form başlığının
        # içinde 'Parola' kelimesinin geçtiği test edilir.
        assert 'Parola' in resp.json['forms']['schema']["title"]
        # Parola hataları için her bir parametre denenir.
        # Doğru hatanın ekranda gösterildiği test edilir.
        for hata in parola_hatalari:
            resp = self.client.post(
                form={parola_parametreleri[0]: hata[0], parola_parametreleri[1]: hata[1],
                      parola_parametreleri[2]: hata[2]})
            assert hata[3] in resp.json["msgbox"]["msg"]

    def test_parola_degistir_basarili_cikis_yapmadan_devam(self):
        # Parola başarılı şekilde değiştirilir.
        self.parola_basarili_degisim()
        # Parola değişikliğinden sonra 'Çıkış Yapmadan Devam Et' seçeneği seçilir.
        resp = self.client.post(form={'devam': 1})
        # Tekrardan profil sayfası görüntüleme ekranına gelindiği test edilir.
        assert 'Profil Sayfası' in resp.json['forms']['schema']["title"]

    def test_kullanici_adi_degistir_basarili_cikis_yapmadan_devam(self):
        # Kullanıcı adı başarılı şekilde değiştirilir.
        self.kullanici_adi_basarili_degisim()
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(self.user_key)
        # Kullanıcı adının değiştiği test edilir.
        assert user.username == 'deneme_kullanici_adi'
        # Kullanıcı adı değişikliğinden sonra 'Çıkış Yapmadan Devam Et' seçeneği seçilir.
        resp = self.client.post(form={'devam': 1})
        # Tekrardan profil sayfası görüntüleme ekranına gelindiği test edilir.
        assert 'Profil Sayfası' in resp.json['forms']['schema']["title"]
        # Profil sayfasında da kullanıcı adının değiştiği test edilir.
        assert resp.json["forms"]["model"]['username'] == 'deneme_kullanici_adi'
        # Kullanıcı adı tekrardan varsayılan haline getirilir.
        user.username = 'ulakbus'
        user.save()

    def test_e_posta_degistir_parola_denemesi_basarisiz(self):
        # E-posta değiştirme iş akışına geçiş yapılır.
        self.client.post(flow="e_posta_degistir")
        # Hatali e_posta adresi girilir.
        resp = self.client.post(form={'e_posta': 'gecersiz_e_posta_adresi'})
        assert 'Girmiş olduğunuz e-posta adresi geçersizdir' in resp.json["msgbox"]["msg"]
        # Geçerli e-posta adresi girilir.
        resp = self.client.post(form={'e_posta': 'ulakbus_mail@ulakbus_mail.com'})
        self.parola_deneme_basarisiz(resp)


    # Test edilecek kısım zato servisini kullandığından yoruma alınmıştır.
    # Zato mock oluştuğunda test edilecektir.

    # def test_e_posta_degistir_link_yolla_basarili(self):
    #     self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
    #     self.client.post()
    #     # E-posta değiştirme iş akışına geçiş yapılır.
    #     self.client.post(flow="e_posta_degistir")
    #     # Geçerli e-posta adresi girilir.
    #     resp = self.client.post(form={'e_posta': 'ulakbus_mail@ulakbus_mail.com'})
    #     # Kullanıcının parolası doğru girilir.
    #     resp = self.client.post(form={'parola': '123'})
    #     # Girilen e-posta adresine doğrulama linki yollanılır ve kullanıcı bilgilendirilir.
    #     # Mail yollandıktan sonra bilgilendirmenin olduğu test edilir.
    #     assert 'E-Posta Doğrulama' == resp.json["msgbox"]["title"]

    def test_parola_degistir_basarili_cikis(self):
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        self.client.post()
        self.client.post(flow="parola_degistir")
        self.parola_basarili_degisim()
        # Kullanıcı adı değişikliğinden sonra 'Çıkış Yap' seçeneği seçilir.
        resp = self.client.post(flow="cikis_yap")
        assert resp.json["cmd"] == 'reload'
        # Kullanıcı adı tekrardan varsayılan haline getirilir.
        user = User.objects.get(self.user_key)
        user.username = 'ulakbus'
        user.save()

    def test_kullanici_adi_degistir_basarili_cikis(self):
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        self.client.post()
        self.client.post(flow="kullanici_adi_degistir")
        self.kullanici_adi_basarili_degisim()
        # Kullanıcı adı değişikliğinden sonra 'Çıkış Yap' seçeneği seçilir.
        resp = self.client.post(flow="cikis_yap")
        assert resp.json["cmd"] == 'reload'
        # Kullanıcı adı tekrardan varsayılan haline getirilir.
        user = User.objects.get(self.user_key)
        user.username = 'ulakbus'
        user.save()

    def test_kullanici_adi_degistir_parola_denemesi_basarisiz(self):
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        self.client.post()
        # Kullanıcı adı değiştirme iş akışına geçiş yapılır.
        resp = self.client.post(flow="kullanici_adi_degistir")
        # Kullanıcı adı değiştirme ekranındaki form başlığının içinde
        # 'Kullanıcı Adı' kelimesinin geçtiği test edilir.
        assert 'Kullanıcı Adı' in resp.json['forms']['schema']["title"]
        # Kullanıcı adı değiştirme hataları için her bir parametre denenir.
        # Doğru hatanın ekranda gösterildiği test edilir.
        for hata in k_adi_hatalari:
            resp = self.client.post(form={k_adi_parametreleri[0]: hata[0],
                                          k_adi_parametreleri[1]: hata[1]})
            assert hata[2] in resp.json["msgbox"]["msg"]

        # Kurallara uygun şekilde kullanıcı adı değiştirme işlemi yapılır.
        # 'ulakbus' olan kullanıcı adı, 'deneme_kullanici_adi' olarak değiştirilir.
        resp = self.client.post(form={k_adi_parametreleri[0]: 'ulakbus',
                                      k_adi_parametreleri[1]: 'deneme_kullanici_adi'})
        # Değişiklik yapabilmek için kullanıcıdan parolasını girmesi istenir.
        self.parola_deneme_basarisiz(resp)

    def test_gecersiz_link(self):
        # İş akışı dışarıdan linkle gelinecek şekilde tekrardan başlatılır.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçersiz olduğu test edilir.
        assert self.client.current.task_data['e_posta'] == None
        # Cache de linkin içerisinde bulunan aktivasyon koduna ait bir bilgi bulunmadığı için
        # linkin geçersiz olduğu mesajın gösterilmesi test edilir.
        assert resp.json['msgbox']['title'] == "Geçersiz İşlem"
        # Değişimden önceki e_postası test sonucunda eskiye döndürmek için kaydedilir.

    def test_gecerli_link_basarili_islem(self):
        # Değiştirilecek e_posta adresi doğrulama kodu keyi ile cache e kaydedilir.
        EPostaDogrulama('2fd1deed4653f40107571368cd46411088c7d988').set(
            'ulakbus_mail@ulakbus_mail.com')
        # Linkle gelerek iş akışı tekrardan başlatılır.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=self.user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Başarılı işlem mesajı oluştuğu test edilir.
        assert resp.json['msgbox']['title'] == 'E-Posta Değişikliği'
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(self.user_key)
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçerliliği test edilir.
        assert self.client.current.task_data['e_posta'] != None
        # Birincil e-posta adresinin değiştiği test edilir.
        assert user.e_mail == 'ulakbus_mail@ulakbus_mail.com'
        # E-postası eski haline döndürülür.
        user.e_mail = self.user.e_mail
        user.save()

    def parola_deneme_basarisiz(self, resp):
        # Kullanıcıdan işlemin tammalanması için parolasının istendiği ekranın geldiği test edilir.
        assert "İşlem Onayı İçin Parola Doğrulama" == resp.json["forms"]["schema"]['title']
        # Kullanıcının parolasını yanlış girmesi durumunda hata mesajının gösterilmesi test edilir.
        for i in range(2):
            resp = self.client.post(form={'parola': 'yanlis_parola'})
            assert 'Hatalı Parola Girişi' in resp.json["msgbox"]["title"]
            assert 'Parolanızı yanlış' in resp.json["msgbox"]["msg"]
        # Parolanın üç kez yanlış girilmesi halinde kullanıcıya
        # zorla çıkış yaptırıldığı test edilir.
        resp = self.client.post(form={'parola': 'yanlis_parola'})
        assert resp.json["cmd"] == 'reload'
        assert 'Hatalı Parola' in resp.json["title"]

    def kullanici_adi_basarili_degisim(self):
        self.client.post(flow="kullanici_adi_degistir")
        # Kurallara uygun şekilde kullanıcı adı değiştirme işlemi yapılır.
        # 'ulakbus' olan kullanıcı adı, 'deneme_kullanici_adi' olarak değiştirilir.
        self.client.post(form={k_adi_parametreleri[0]: 'ulakbus',
                               k_adi_parametreleri[1]: 'deneme_kullanici_adi'})
        resp = self.client.post(form={'parola': '123'})
        # Başarılı işlemden sonra 'İşlem Seçeneği' başlığı olduğu test edilir.
        assert "İşlem Seçeneği" == resp.json["forms"]["schema"]['title']

    def parola_basarili_degisim(self):
        # Kurallara uygun şekilde parola değiştirme işlemi yapılır.
        # Uygun parola en az bir büyük harf, bir küçük harf, bir sayı
        # ve bir özel karakterin bulunduğu 'Parola3*' parolasıdır.
        resp = self.client.post(
            form={parola_parametreleri[0]: '123', parola_parametreleri[1]: 'Parola3*',
                  parola_parametreleri[2]: 'Parola3*'})

        # Başarılı işlemden sonra 'İşlem Seçeneği' başlığı olduğu test edilir.
        assert "İşlem Seçeneği" == resp.json["forms"]["schema"]['title']
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(self.user_key)
        # Parolanın değiştiği test edilir.
        assert user.check_password('Parola3*')
        # Parola tekrardan varsayılan hale getirilir.
        user.password = "123"
        user.save()
