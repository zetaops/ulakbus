# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User
from zengine.lib.test_utils import BaseTestCase
from ulakbus.lib.common import ParolaSifirlama
from .test_profil_sayfasi_goruntuleme import parola_hatalari


class TestCase(BaseTestCase):
    user_key = 'iG4mvjQrfkvTDvM6Jk56X5ILoJ'
    user = User.objects.get(user_key)
    user.username = 'ulakbus'
    user.password = '123'
    user.e_mail = 'ulakbus_deneme_maili@ulakbus_deneme.com'
    user.save()

    def test_aktivasyon_link_yollama(self):
        # ulakbus kullanıcısıyla giriş yapılır.
        # Test edilecek iş akışı seçilir.
        self.prepare_client('/parolami_unuttum', user=self.user)
        resp = self.client.post()
        # Linkle gelinmenin olmadığı test edilir.
        assert self.client.current.task_data['link'] == False
        # Linkle gelinme yoksa Parola Sıfırlama ekranının görüntülenmesi test edilir.
        assert 'Parola Sıfırlama' == resp.json['forms']['schema']["title"]
        # Veritabanında bulunmayan bir kullanıcı adı verilir, Hatalı Bilgi
        # başlıklı hata mesaj kutusu oluşması test edilir.
        resp = self.client.post(form={'kullanici_adi': 'boyle_bir_kullanici_adi_yok'})
        assert resp.json['msgbox']['title'] == 'Hatalı Bilgi'

        # Test edilecek kısım zato servisini kullandığından yoruma alınmıştır.
        # Zato mock oluştuğunda test edilecektir.

        # # Veritabanında bulunan ve birincil e-postası kayıtlı olan kullanıcı
        # # adı verildiğinde doğrulama linkinin yollandığını gösteren mesaj
        # # kutusunun oluşması test edilir.
        # resp = self.client.post(form={'kullanici_adi': 'ulakbus'})
        # assert resp.json['msgbox']['title'] == 'E-Posta Doğrulama'

    def gecersiz_link_gelisi(self):
        # İş akışı dışarıdan linkle gelinecek şekilde tekrardan başlatılır.
        self.prepare_client('/parolami_unuttum', user=self.user)
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçersiz olduğu test edilir.
        assert self.client.current.task_data['kullanici_key'] == None
        # Cache de linkin içerisinde bulunan aktivasyon koduna ait bir bilgi bulunmadığı için
        # linkin geçersiz olduğu mesajın gösterilmesi test edilir.
        assert resp.json['msgbox']['title'] == "Geçersiz İşlem"
        # Değişimden önceki e_postası test sonucunda eskiye döndürmek için kaydedilir.

    def gecerli_link_gelisi(self):
        # Linkle gelerek iş akışı tekrardan başlatılır.
        self.prepare_client('/parolami_unuttum', user=self.user)
        # Parolası sıfırlanacak kullanıcının keyi doğrulama kodu ile cache e kaydedilir.
        ParolaSifirlama('2fd1deed4653f40107571368cd46411088c7d988').set(
            'iG4mvjQrfkvTDvM6Jk56X5ILoJ')
        resp = self.client.post(model='dogrulama=2fd1deed4653f40107571368cd46411088c7d988')
        # Başarılı işlem mesajı oluştuğu test edilir.
        assert resp.json['msgbox']['title'] == "E-Posta Adresi Doğrulama İşlemi"
        # Linkle gelindiği test edilir.
        assert self.client.current.task_data['link'] == True
        # Linkin geçerliliği test edilir.
        assert self.client.current.task_data['kullanici_key'] != None

        # Parola değiştirme ekranındaki form başlığının içinde 'Parola' kelimesinin
        # geçtiği test edilir.
        assert 'Parola' in resp.json['forms']['schema']["title"]
        parola_parametreleri = ['yeni_parola', 'yeni_parola_tekrar']

        # Eski parola ile yapılacak kontroller kontrol listesinden kaldırılır.
        del parola_hatalari[0]
        del parola_hatalari[1]
        # Parola hataları için her bir parametre denenir.
        # Doğru hatanın ekranda gösterildiği test edilir.
        for hata in parola_hatalari:
            resp = self.client.post(
                form={parola_parametreleri[0]: hata[1], parola_parametreleri[1]: hata[2]})
            assert hata[3] in resp.json["msgbox"]["msg"]

        # Kurallara uygun şekilde parola değiştirme işlemi yapılır.
        resp = self.client.post(form={parola_parametreleri[0]: 'Parola3*',
                                      parola_parametreleri[1]: 'Parola3*'})
        # Parola değişikliği gerçekleştikten sonra kullanıcının yeni şifresiyle giriş yapabilmesi
        # için giriş yapma ekranına yönlendirildiği kontrol edilir.
        assert resp.json['cmd'] == 'reload'
        assert resp.json['title'] == 'Parolanız Başarıyla Sıfırlandı'
        # Veritabanından kullanıcı tekrar çekilir.
        user = User.objects.get(self.user_key)
        # Parolanın değiştiği test edilir.
        assert user.check_password('Parola3*')
        # Parola tekrardan varsayılan hale getirilir.
        user.password = "123"
        user.blocking_save()
        # Bilginin cache den silindiği test edilir.
        assert ParolaSifirlama('2fd1deed4653f40107571368cd46411088c7d988').get() == None
        # Parola sıfırlanması için kullanılan linkle iş akışı tekrar başlatılır.
        # İşlemi gerçekleştikten sonra linkin geçerliliğini kaybettiği kontrol edilir.
        self.gecersiz_link_gelisi()
