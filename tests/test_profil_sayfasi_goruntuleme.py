# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from zengine.lib import translation
import random
from zengine.lib.cache import EMailVerification


class TestCase(BaseTestCase):
    def test_profil_sayfasi_goruntuleme(self):
        # ulakbus kullanıcısıyla giriş yapılır.
        user = User.objects.get(username='ulakbus')
        user_key = user.key
        # Test edilecek iş akışı seçilir.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=user)
        resp = self.client.post()
        # Linkle gelinmenin olmadığı test edilir.
        assert self.client.current.task_data['link'] == False
        # Profil sayfasının görüntülenmesi test edilir.
        assert 'Profil Sayfası' in resp.json['forms']['schema']["title"]

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

        # Parola değiştirme iş akışına geçiş yapılır.
        resp = self.client.post(flow="parola_degistir")
        # Parola değiştirme ekranındaki form başlığının içinde 'Parola' kelimesinin
        # geçtiği test edilir.
        assert 'Parola' in resp.json['forms']['schema']["title"]
        parola_parametreleri = ['eski_parola', 'yeni_parola', 'yeni_parola_tekrar']
        parola_hatalari = [('parola', 'parola', 'parola', 'Kullanmakta'), ('123', 'paro', 'paro', 'en az 8'),
                           ('123', 'parolaparo', 'parolaparo', 'özel karakter'),
                           ('123', 'parola**', 'parola**', 'bir küçük harf'),
                           ('123', 'paro', 'parola', 'uyuşmamaktadır')]
        # Parola hataları için her bir parametre denenir.
        # Doğru hatanın ekranda gösterildiği test edilir.
        for hata in parola_hatalari:
            resp = self.client.post(form={parola_parametreleri[0]: hata[0], parola_parametreleri[1]: hata[1],
                                          parola_parametreleri[2]: hata[2]})
            assert hata[3] in resp.json["msgbox"]["msg"]

        # Kurallara uygun şekilde parola değiştirme işlemi yapılır.
        resp = self.client.post(form={parola_parametreleri[0]: '123', parola_parametreleri[1]: 'Parola3*',
                                      parola_parametreleri[2]: 'Parola3*'})

        # Başarılı işlemden sonra 'İşlem Bilgilendirme' başlığı olduğu test edilir.
        assert "İşlem Bilgilendirme" == resp.json["forms"]["schema"]['title']
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(user_key)
        # Parolanın değiştiği test edilir.
        assert user.check_password('Parola3*')
        # Parola tekrardan varsayılan hale getirilir.
        user.password = "123"
        user.save()
        # Parola değişikliğinden sonra 'Çıkış Yapmadan Devam Et' seçeneği seçilir.
        resp = self.client.post(form={'devam': 1})
        # Tekrardan profil sayfası görüntüleme ekranına gelindiği test edilir.
        assert 'Profil Sayfası' in resp.json['forms']['schema']["title"]

        # Kullanıcı adı değiştirme iş akışına geçiş yapılır.
        resp = self.client.post(flow="kullanici_adi_degistir")
        # Kullanıcı adı değiştirme ekranındaki form başlığının içinde 'Kullanıcı Adı' kelimesinin
        # geçtiği test edilir.
        assert 'Kullanıcı Adı' in resp.json['forms']['schema']["title"]
        k_adi_parametreleri = ['eski_k_adi', 'yeni_k_adi']
        k_adi_hatalari = [('slmdalsmdlsa', 'saldmsadmlsam', 'Kullanıcı adınızı yanlış'),
                          ('ulakbus', 'ulakbus', 'aynı olmamalıdır')]

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

        # Başarılı işlemden sonra 'İşlem Bilgilendirme' başlığı olduğu test edilir.
        assert "İşlem Bilgilendirme" == resp.json["forms"]["schema"]['title']
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(user_key)
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

        # E-Posta değiştirme iş akışına geçiş yapılır.
        resp = self.client.post(flow="e_posta_degistir")
        # E-Posta değiştirme ekranındaki form başlığının içinde 'E-Posta' kelimesinin
        # geçtiği test edilir.
        assert 'E-Posta' in resp.json['forms']['schema']["title"]
        # Birincil olacak e-posta adresi girilir.
        assert user.e_mail != 'ulakbus_mail@ulakbus_mail.com'
        resp = self.client.post(form={'e_posta': 'ulakbus_mail@ulakbus_mail.com'})
        # Girilen e-posta adresine doğrulama linki yollanılır ve kullanıcı bilgilendirilir.
        # Mail yollandıktan sonra bilgilendirmenin olduğu test edilir.
        assert 'E-Posta Doğrulama' == resp.json["msgbox"]["title"]

        # İş akışı dışarıdan linkle gelinecek şekilde tekrardan başlatılır.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçersiz olduğu test edilir.
        assert self.client.current.task_data['gecerli'] == False
        # Cache de linkin içerisinde bulunan aktivasyon koduna ait bir bilgi bulunmadığı için
        # linkin geçersiz olduğu mesajın gösterilmesi test edilir.
        assert resp.json['msgbox']['title'] == "Geçersiz İşlem"
        # Değişimden önceki e_postası test sonucunda eskiye döndürmek için kaydedilir.
        birincil_e_posta = user.e_mail

        # Değiştirilecek e_posta adresi doğrulama kodu keyi ile cache e kaydedilir.
        EMailVerification('2fd1deed4653f40107571368cd46411088c7d988').set('ulakbus_mail@ulakbus_mail.com')
        # Linkle gelerek iş akışı tekrardan başlatılır.
        self.prepare_client('/profil_sayfasi_goruntuleme', user=user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Başarılı işlem mesajı oluştuğu test edilir.
        assert resp.json['msgbox']['title'] == 'E-Posta Değişikliği'
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(user_key)
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçerliliği test edilir.
        assert self.client.current.task_data['gecerli'] == True
        # Birincil e-posta adresinin değiştiği test edilir.
        assert user.e_mail == 'ulakbus_mail@ulakbus_mail.com'
        # E-postası eski haline döndürülür.
        user.e_mail = birincil_e_posta
        user.save()
