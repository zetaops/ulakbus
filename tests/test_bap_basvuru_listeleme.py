# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje, User
from ulakbus.models import Role
from zengine.lib.test_utils import BaseTestCase
from zengine.models import WFInstance, Message
import time


class TestCase(BaseTestCase):
    """
    BAP Projeleri listeleme, inceleme ve karar verme iş akışlarının testlerini içerir.

    """

    def test_bap_basvuru_listeleme(self):
        # Proje alınır.
        project = BAPProje.objects.get('WlRiJzMM4XExfmbgVyJDBZAUGg')
        # Öğretim üyesi kullanıcısı alınır.
        user_ou = User.objects.get(username='ogretim_uyesi_1')
        # Koordinasyon birimi kullanıcısı kullanıcısı alınır.
        user_koord = User.objects.get(username='bap_koordinasyon_birimi_1')
        # İlgili projenin oluşturulduğu(başvuru) wf instance'ı alınır.
        wfi = WFInstance.objects.get(wf_object=project.key, finished=True)
        # Instance'da kayıtlı bulunan formda proje adı kısmı Akıllı Robot olduğu kontrol edilir.
        assert wfi._data['data']['GenelBilgiGirForm']['ad'] == 'Akıllı Robot'
        # Projenin son durumu 4 yani onaylanmış olduğu kontrol edilir.
        assert project.durum == 4
        # WF Instance stepinin End olduğu yani iş akışının bitmiş olduğu kontrol edilir.
        assert 'End' in wfi.step
        # Koordinasyon birimi başvuru listeleme iş akışını başlatır.
        self.prepare_client('/bap_basvuru_listeleme', user=user_koord)
        resp = self.client.post()
        # Listeleme ekranının başlığının BAP Projeler olduğu kontrol edilir.
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        # Listeleme kategorileri kontrol edilir.
        # assert u'Proje_Adı' in resp.json['objects'][0]
        assert 'Okutman' in resp.json['objects'][0]

        # Seçilen projenin adının da listeleme ekranında bulunduğu kontrol edilir.
        del resp.json['objects'][0]
        project_name_list = [obj['fields'][0] for obj in resp.json['objects']]
        assert "Akıllı Robot" in project_name_list

        # Komisyon üyesi atama bölümü
        komisyon_uyesi_role_key = "GbviU7cmCejVzjO8IB8LV6WCGIf" # Dirican Seven
        komisyon_uyesi = Role.objects.get(komisyon_uyesi_role_key)
        self.client.post(cmd='komisyon_uyesi_atama', object_id=project.key)
        resp = self.client.post(form={'komisyon_uyesi': komisyon_uyesi_role_key,
                                      'ilerle': 1})
        assert resp.json['forms']['form'][0]['helpvalue'] == "%s projesine %s " \
                                                              "komisyon üyesini atayacaksınız." % \
                                                              (project.ad, komisyon_uyesi.user())
        resp = self.client.post(form={'onayla': 1})

        assert resp.json['forms']['form'][0]['helpvalue'] == "%s projesine %s adlı komisyon " \
                                                              "üyesini başarıyla atadınız." % \
                                                              (project.ad, komisyon_uyesi.user())
        self.client.post(form={'tamam': 1})

        resp = self.client.post(cmd='komisyon_uyesi_atama', object_id=project.key)
        assert resp.json['forms']['form'][0]['helpvalue'] == "%s projesinin zaten bir komisyon " \
                                                             "üyesi bulunmaktadır. Mevcut " \
                                                             "komisyon üyesinin ismi: %s 'dir. " \
                                                             "Eğer mevcut komisyon üyesinin " \
                                                             "yerine bir başkasını atamak " \
                                                             "istiyorsanız işleme devam ediniz." % \
                                                             (project.ad, komisyon_uyesi.user())
        resp = self.client.post(cmd='iptal', form={'iptal': 1})
        assert resp.json['forms']['form'][0]['helpvalue'] == "Başvuru listeleme ekranına " \
                                                             "geri dönüyorsunuz"
        self.client.post(form={'tamam': 1})

        # Seçilen proje için işlem geçmişi butonuna basılır ve projenin işlem geçmişi görüntülenir.
        resp = self.client.post(cmd='islem_gecmisi', object_id=project.key,
                                wf="bap_basvuru_listeleme")

        # Proje işlem geçmişinin başlığı kontrol edilir.
        assert resp.json['forms']['schema']['title'] == 'Proje İşlem Geçmişi'
        # Tablo başlıkları kontrol edilir.
        assert 'Eylem' in resp.json['objects'][0]
        assert 'Açıklama' in resp.json['objects'][0]
        assert 'Tarih' in resp.json['objects'][0]

        # Tekrardan listeleme ekranına geri dönülür.
        resp = self.client.post(wf='bap_basvuru_listeleme', form={'geri': 1})
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'

        # Seçilen proje için incele butonuna basılır ve inceleme iş akışı tetiklenir.
        resp = self.client.post(cmd='incele', object_id=project.key,
                                wf="bap_basvuru_listeleme")

        # İnceleme iş akışının default sayfası Proje Hakkında olmalıdır. Başlık kontrol edilir.
        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'
        # Proje hakkında sayfası'nda proje hakkında istenilen bilgilerin olduğu kontrol edilir.
        assert 'Proje Adı' in resp.json['object'].keys()
        # Proje adı kısmı Akıllı Robot olmalıdır.
        assert resp.json['object']['Proje Adı'] == 'Akıllı Robot'
        # Araştırma Olanakları detay kısmı kontrolleri
        resp = self.client.post(cmd='olanak', wf="bap_basvuru_listeleme")
        assert 'Demirbaş' in resp.json['objects'][0]
        assert resp.json['forms']['schema']['title'] == 'Araştırma Olanakları'
        # Üniversite Dışı Uzmanlar detay kısmı kontrolleri
        resp = self.client.post(cmd='dis_uzman', wf="bap_basvuru_listeleme")
        assert 'Kurum' in resp.json['objects'][0]
        assert resp.json['forms']['schema']['title'] == 'Üniversite Dışı Uzmanlar'
        # Üniversite Dışı Destekler detay kısmı kontrolleri
        resp = self.client.post(cmd='dis_destek', wf="bap_basvuru_listeleme")
        assert resp.json['forms']['schema']['title'] == 'Üniversite Dışı Destekler'

        # Detay ekranından geri dönüldüğünde genel proje bilgilerinin gösterildiği
        # ekrana gidildiği kontrol edilir.
        resp = self.client.post(cmd='geri_don', wf="bap_basvuru_listeleme")
        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'

        # Projenin bütçe planı kısmı kontrol edilir.
        resp = self.client.post(cmd='butce_plani', wf='bap_basvuru_listeleme',
                                form={'butce': 1})
        assert resp.json['forms']['schema']['title'] == 'Bütçe Planı'
        assert 'Muhasebe Kodu' and 'Kod Adı' in resp.json['objects'][0]

        # Projenin proje çalışanları kısmı kontrol edilir.
        resp = self.client.post(cmd='proje_calisanlari', wf='bap_basvuru_listeleme',
                                form={'proje_calisanlari': 1})
        assert 'Çalışmaya Katkısı' in resp.json['objects'][0]
        assert resp.json['forms']['schema']['title'] == 'Proje Çalışanları'

        # Projenin  iş planı kısmı kontrol edilir.
        resp = self.client.post(cmd='is_plani', wf='bap_basvuru_listeleme', form={'is_plani': 1})
        assert 'Paket Adı' in resp.json['objects'][0]
        assert resp.json['forms']['schema']['title'] == 'İş Planı'

        # İş planları arasından bir planın ayrıntılarını görme kısmı kontrol edilir.
        resp = self.client.post(cmd='ayrinti', wf='bap_basvuru_listeleme',
                                data_key='QFf918chMLclolXnMbbF56NAbxd')
        assert resp.json['forms']['schema']['title'] == 'Robot Yazılımı İş Planı Ayrıntıları'

        # Tekrardan iş planı kısmına dönüldüğü kontrol edilir.
        resp = self.client.post(wf='bap_basvuru_listeleme', form={'geri': 1})
        assert resp.json['forms']['schema']['title'] == 'İş Planı'

        # Daha sonra karar ver seçeneğine tıklandığında tekrardan listeleme ekranına dönüldüğü
        # kontrol edilir.
        resp = self.client.post(cmd='iptal', wf='bap_basvuru_listeleme', form={'iptal': 1})
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'

        # Tekrardan projeyi inceleye tıklanılır.
        self.client.post(cmd='incele', object_id=project.key, wf="bap_basvuru_listeleme")

        # Karar ver butonuna tıklanarak karar verme iş akışı tetiklenilir.
        resp = self.client.post(cmd='karar_ver', wf='bap_basvuru_listeleme', form={'karar_ver': 1})
        assert resp.json['forms']['schema']['title'] == "İnceleme Sonrası Proje Kararı"
        assert 'Henife Şener' and 'Akıllı Robot' in resp.json['forms']['form'][0]['helpvalue']

        # Burada da daha sonra karar ver seçeneğine tıklandığında tekrardan listeleme
        # ekranına dönüldüğü kontrol edilir.
        resp = self.client.post(cmd='iptal', wf='bap_basvuru_listeleme', form={'iptal': 1})
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        self.client.post(cmd='incele', object_id=project.key, wf="bap_basvuru_listeleme")
        self.client.post(cmd='karar_ver', object_id=project.key, form={'karar_ver': 1})
        # Projenin sahibi öğretim görevlisinden revizyon istenir.
        resp = self.client.post(cmd='revizyon', wf='bap_basvuru_listeleme', form={'revizyon': 1})
        # Revizyon gerekçesi 'test-revizyon-gerekçe' olarak girilir.
        assert resp.json['forms']['schema']['title'] == "Revizyon İsteme Gerekçeleri"
        resp = self.client.post(cmd='gonder', wf='bap_basvuru_listeleme',
                                form={'gonder': 1, 'revizyon_gerekce': 'test-revizyon-gerekçe'})
        # Başarılı işlem mesajı kontrol edilir.
        assert resp.json['msgbox']['title'] == "Kararınız İletildi"
        assert 'Henife Şener' and 'Akıllı Robot' in resp.json['msgbox']['msg']
        # Tekrardan listeleme ekranına dönüldüğü kontrol edilir.
        assert resp.json['forms']['schema']['title'] == 'BAP Projeler'
        project.reload()
        wfi.reload()
        # Projenin durumu 3 yani revizyonda olduğu kontrol edilir.
        assert project.durum == 3
        # Instance field'larının değiştiği kontrol edilir.
        assert wfi.finished == False
        assert 'bap' in wfi.step
        # Koordinasyon birimi kullanıcısından çıkış yapılır.
        self.client.post(wf='logout')

        # Öğretim üyesi kullanıcısıyla token ile giriş yapılır.
        self.prepare_client('/bap_proje_basvuru', user=user_ou, token=wfi.key)
        resp = self.client.post()
        # Projenın adı ve yollanan revizyon gerekçesinin doğruluğu kontrol edilir.
        assert 'Akıllı Robot' in resp.json['forms']['schema']['title']
        assert 'Revizyon Gerekçeleri' and 'test-revizyon-gerekçe' in resp.json['forms']['form'][0][
            'helpvalue']
        # Revize et denilir.
        resp = self.client.post(wf='bap_proje_basvuru', form={'devam': 1})
        # Proje fieldlarının dolu olarak geldiği kontrol edilir.
        assert resp.json['forms']['schema']['title'] == "Proje Türü Seçiniz"
        self.client.post(cmd='kaydet_ve_kontrol', wf='bap_proje_basvuru', form={'sec': 1})

        resp = self.client.post(cmd='genel', wf='bap_proje_basvuru', form={'belgelerim_hazir': 1})
        assert resp.json['forms']['schema']['title'] == "Proje Genel Bilgileri"
        assert resp.json['forms']['model']['ad'] == 'Akıllı Robot'
        # Proje adı Otomatik Süpürge olarak değiştirilir.
        resp = self.client.post(wf='bap_proje_basvuru',
                                form={'ad': 'Otomatik Süpürge',
                                      'detay_gir': 1}, cmd='detay_gir')
        assert resp.json['forms']['schema']['title'] == 'Proje Detayları'
        assert 'Lorem ipsum' in resp.json['forms']['model']['hedef_ve_amac']
        resp = self.client.post(wf='bap_proje_basvuru', form={'proje_belgeleri': 1})
        assert resp.json['forms']['schema']['title'] == 'Proje Belgeleri'
        resp = self.client.post(wf='bap_proje_basvuru', form={'arastirma_olanaklari': 1})
        assert resp.json['forms']['schema']['title'] == 'Araştırma Olanakları Ekle'
        assert 'Endüstriyel' in resp.json['forms']['model']['Olanak'][0]['ad']
        resp = self.client.post(cmd='ilerle', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Çalışan Ekle"
        assert resp.json['forms']['model']['Calisan'][0]['ad'] == 'Kerim'

        resp = self.client.post(cmd='ileri', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Üniversite Dışı Uzman Ekle"
        resp = self.client.post(wf='bap_proje_basvuru', cmd='ileri', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Bap İş Paketi Takvimi"
        resp = self.client.post(wf='bap_proje_basvuru', cmd='bitir', form={'bitir': 1})

        assert resp.json['forms']['schema']['title'] == "Üniversite Dışı Destek Ekle"
        resp = self.client.post(wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Otomatik Süpürge projesi için Bütçe Planı"
        resp = self.client.post(wf='bap_proje_basvuru', cmd='bitir', form={'bitir': 1})

        assert resp.json['forms']['schema']['title'] == "Yürütücü Tecrübesi"
        resp = self.client.post(cmd='ileri', wf='bap_proje_basvuru', form={'ileri': 1})
        assert resp.json['forms']['schema']['title'] == "Yürütücünün Halihazırdaki Projeleri"
        resp = self.client.post(cmd="ileri", wf='bap_proje_basvuru',
                                form={'ileri': 1, 'form_name': "YurutucuProjeForm"})
        assert resp.json['forms']['schema']['title'] == "Proje Gerçekleştirme Görevlisi Seçimi"
        resp = self.client.post(wf='bap_proje_basvuru',
                                form={'sec': 1, 'form_name': "GerceklestirmeGorevlisiForm"})

        # Revize edildikten sonra onaya göndermeden önceki gösterimde
        # projenin adının değiştiği kontrol edilir.
        assert 'Otomatik Süpürge' in resp.json['object_title']
        assert resp.json['object'][u'Proje Adı'] == u'Otomatik Süpürge'
        # Onaya gönderilir.
        resp = self.client.post(cmd='onay', wf='bap_proje_basvuru', form={'ileri': 1})
        # Başarılı işlem mesajı kontrol edilir.
        assert resp.json['msgbox']['title'] == "Başvurunuzu tamamladınız!"

        project.reload()
        # Projenin durumu 2 yani koordinasyon biriminin onayına gönderildi olarak
        # değiştiği kontrol edilir.
        assert project.durum == 2
        # Çıkış yapılır.
        self.client.post(wf='logout')

        # Koordinasyon birimi olarak tekrardan giriş yapılır.
        self.prepare_client('/bap_basvuru_listeleme', user=user_koord, token=wfi.key)
        resp = self.client.post()
        # Projenin adının değiştiği kontrol edilir.
        assert resp.json['forms']['schema']['title'] == 'Proje Hakkında'
        assert resp.json['object']['Proje Adı'] == 'Otomatik Süpürge'
        # Karar verilir.
        resp = self.client.post(cmd='karar_ver', wf='bap_basvuru_listeleme', form={'karar_ver': 1})
        assert resp.json['forms']['schema']['title'] == "İnceleme Sonrası Proje Kararı"
        # Revizyondan gelen proje onaylanır.
        resp = self.client.post(cmd='onayla', wf='bap_basvuru_listeleme', form={'karar_ver': 1})
        # Projenin değişmiş adının onay ekranında olduğu kontrol edilir.
        assert 'Otomatik Süpürge' in resp.json['forms']['schema']['title']
        assert 'Otomatik Süpürge' in resp.json['forms']['form'][0]['helpvalue']
        self.client.post(cmd='onayla', wf='bap_basvuru_listeleme', form={'tamam': 1})

        time.sleep(1)
        # Öğretim elemanına projenin onaylandığına dair bildirim gittiği kontrol edilir.
        notification = Message.objects.filter().order_by()[0]
        project.reload()
        wfi.reload()
        # Projenin durumu 4 yani onaylanmış olduğu kontrol edilir.
        assert project.durum == 4

        # sync_wf_cache methodunun bg_job olarak çalışması için worker'a ihtiyaç olduğu için wfi
        # kısmı kontrolü yoruma alındı, bu methodun çalışması için çözüm bulunacak.

        # Instance'ın finished field'ının tekrardan True olduğu kontrol edilir.
        # assert wfi.finished == True
        # Instance'ın step field'ı End olmalı.
        # assert 'End' in wfi.step

        # Öğretim görevlisine giden bildirimde projenin adı değişmiş olan olmalıdır.
        assert 'Otomatik Süpürge' in notification.msg_title
        assert 'gündeme alınmıştır' in notification.body
        # Bildirimi gönderenin koordinasyon birimi kullanıcısının olduğu kontrol edilir.
        assert notification.sender.key == user_koord.key
        # Bildirimi alanın öğretim görevlisi kullanıcısının olduğu kontrol edilir.
        assert notification.receiver.key == user_ou.key
        # Instance içinde bulunan form datasında proje adı kısmının değişmiş olduğu kontrol edilir.
        assert wfi._data['data']['GenelBilgiGirForm']['ad'] == 'Otomatik Süpürge'

        # Test sonunda değişen kısımlar default haline döndürülür.
        wfi._data['data']['GenelBilgiGirForm']['ad'] = 'Akıllı Robot'
        wfi.finished = True
        wfi.step = '"EndEvent_bap_project.ToEndJoin", 1'
        wfi.save()
        project.ad = 'Akıllı Robot'
        project.save()
        BAPProje.objects.filter(durum=None).delete()
