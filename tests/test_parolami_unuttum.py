# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from zengine.lib.cache import PasswordReset


class TestCase(BaseTestCase):
    def test_parolami_unuttum(self):
        # ulakbus kullanıcısıyla giriş yapılır.
        user = User.objects.get(username='ulakbus')
        user_key = user.key
        # Test edilecek iş akışı seçilir.
        self.prepare_client('/parolami_unuttum', user=user)
        resp = self.client.post()
        # Linkle gelinmenin olmadığı test edilir.
        assert self.client.current.task_data['link'] == False
        # Linkle gelinme yoksa profil sayfasının görüntülenmesi test edilir.
        assert 'Parola Sıfırlama' == resp.json['forms']['schema']["title"]
        # Veritabanında bulunmayan bir kullanıcı adı verilir, Hatalı Bilgi
        # başlıklı hata mesaj kutusu oluşması test edilir.
        resp = self.client.post(form={'kullanici_adi': 'boyle_bir_kullanici_adi_yok'})
        assert resp.json['msgbox']['title'] == 'Hatalı Bilgi'
        # Veritabanında bulunan ve birincil e-postası kayıtlı olan kullanıcı
        # adı verildiğinde doğrulama linkinin yollandığını gösteren mesaj
        # kutusunun oluşması test edilir.
        resp = self.client.post(form={'kullanici_adi': 'ulakbus'})
        assert resp.json['msgbox']['title'] == 'E-Posta Doğrulama'

        # İş akışı dışarıdan linkle gelinecek şekilde tekrardan başlatılır.
        self.prepare_client('/parolami_unuttum', user=user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçersiz olduğu test edilir.
        assert self.client.current.task_data['gecerli'] == False
        # Cache de linkin içerisinde bulunan aktivasyon koduna ait bir bilgi bulunmadığı için
        # linkin geçersiz olduğu mesajın gösterilmesi test edilir.
        assert resp.json['msgbox']['title'] == "Geçersiz İşlem"
        # Değişimden önceki e_postası test sonucunda eskiye döndürmek için kaydedilir.


        # Linkle gelerek iş akışı tekrardan başlatılır.
        self.prepare_client('/parolami_unuttum', user=user)
        # Parolası sıfırlanacak kullanıcının keyi doğrulama kodu ile cache e kaydedilir.
        PasswordReset('2fd1deed4653f40107571368cd46411088c7d988').set('iG4mvjQrfkvTDvM6Jk56X5ILoJ')
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Başarılı işlem mesajı oluştuğu test edilir.
        assert resp.json['msgbox']['title'] == "E-Posta Adresi Doğrulama İşlemi"
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçerliliği test edilir.
        assert self.client.current.task_data['gecerli'] == True

        # Parola değiştirme ekranındaki form başlığının içinde 'Parola' kelimesinin
        # geçtiği test edilir.
        assert 'Parola' in resp.json['forms']['schema']["title"]
        parola_parametreleri = ['yeni_parola', 'yeni_parola_tekrar']
        parola_hatalari = [('paro', 'paro', 'en az 8'),
                           ('parolaparo', 'parolaparo', 'özel karakter'),
                           ('parola**', 'parola**', 'bir küçük harf'),
                           ('paro', 'parola', 'uyuşmamaktadır')]
        # Parola hataları için her bir parametre denenir.
        # Doğru hatanın ekranda gösterildiği test edilir.
        for hata in parola_hatalari:
            resp = self.client.post(form={parola_parametreleri[0]: hata[0], parola_parametreleri[1]: hata[1]})
            assert hata[2] in resp.json["msgbox"]["msg"]

        # Kurallara uygun şekilde parola değiştirme işlemi yapılır.
        resp = self.client.post(form={parola_parametreleri[0]: 'Parola3*',
                                      parola_parametreleri[1]: 'Parola3*'})

        # Başarılı işlemden sonra 'İşlem Bilgilendirme' başlığı olduğu test edilir.
        assert "İşlem Bilgilendirme" == resp.json["forms"]["schema"]['title']
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(user_key)
        # Parolanın değiştiği test edilir.
        assert user.check_password('Parola3*')
        # Parola tekrardan varsayılan hale getirilir.
        user.password = "123"
        user.blocking_save()
        # Bilginin cache den silindiği test edilir.
        assert PasswordReset('2fd1deed4653f40107571368cd46411088c7d988').get() == None
        # Değişen parola ile giriş yapılabilmesi giriş ekranına gidilir.
        resp = self.client.post(form={'giris_yap': 1})
