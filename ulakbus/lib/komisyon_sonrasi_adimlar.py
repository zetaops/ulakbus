# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.common import is_akisini_belli_bir_adimdan_aktif_et
from ulakbus.models import BAPButcePlani, BAPRapor, Okutman, Permission, User, BAPSatinAlma, \
    BAPGenel
from zengine.lib.translation import gettext as _
from datetime import datetime, timedelta
from zengine.models import WFInstance, BPMNWorkflow, TaskInvitation
import json

gundem_kararlari = {
    1: {'tip_adi': 'proje_basvurusu',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red'), ('revizyon', 'Revizyon')],
        'default': 'kabul'},
    2: {'tip_adi': 'ek_butce_talebi',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
    3: {'tip_adi': 'fasil_aktarim_talebi',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
    4: {'tip_adi': 'ek_sure_talebi',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
    5: {'tip_adi': 'proje_sonuc_raporu',
        'kararlar': [('basarili', 'Başarılı'), ('basarisiz', 'Başarısız')],
        'default': 'basarili'},
    6: {'tip_adi': 'proje_donem_raporu',
        'kararlar': [('basarili', 'Başarılı'), ('basarisiz', 'Başarısız')],
        'default': 'basarili'},
    7: {'tip_adi': 'proje_iptal_talebi',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
    8: {'tip_adi': 'yurutucu_degisikligi',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
    9: {'tip_adi': 'etkinlik_basvuru',
        'kararlar': [('kabul', 'Kabul'), ('red', 'Red')],
        'default': 'kabul'},
}


class KomisyonKarariSonrasiAdimlar():
    def __init__(self, obj, user):
        self.object = obj
        self.user = user

    def proje_basvurusu_kabul(self):
        """
        Projenin durumu komisyon tarafından onaylandı anlamına gelen 5 yapılır.
    
        """
        eylem = "Onaylandı"
        aciklama = "Proje, komisyon tarafından {} karar numarası ile onaylandı."
        self.islem_gecmisi_guncelle(eylem, aciklama, durum=5)
        self.butce_kalemleri_durum_degistir(durum=2)

        bildirim = _(
            u"%s adlı projeniz %s karar numarası ile komisyon tarafından onaylanmıştır.") % (
                       self.object.proje.ad, self.object.karar_no)

        self.bildirim_gonder(bildirim)
        self.butce_fisi_is_akisini_tetikle()

    def proje_basvurusu_red(self):
        """
        Projenin durumu komisyon tarafından reddedildi anlamına gelen 6 yapılır.

        """
        eylem = "Reddedildi"
        aciklama = "Proje komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama, durum=6)
        self.butce_kalemleri_durum_degistir(durum=3)

        bildirim = _(
            u"%s adlı projeniz %s karar numarası ile komisyon tarafından reddedilmiştir. Gerekçe:"
            u" %s") % (self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def proje_basvurusu_revizyon(self):
        """
        Projenin durumu komisyon tarafından revizyon istendi anlamına gelen 7 yapılır. 
        Öğretim üyesine davet gönderilerek, projesini revize etmesi sağlanır.

        """
        eylem = "Revizyon"
        aciklama = "Proje, komisyon tarafindan {} karar numarası ile revizyona gonderildi."
        self.islem_gecmisi_guncelle(eylem, aciklama, durum=7)

        role = self.object.proje.basvuru_rolu
        data = {'karar': 'revizyon',
                'revizyon_gerekce': self.object.karar_gerekce}
        step = '"bap_revizyon_noktasi", 1'
        title = _(u"Proje Revizyon İsteği")
        message = _(u"""%s adlı başvurunuza komisyon tarafından %s karar numarası ile 
        revizyon istenmiştir. Görev yöneticinizden ilgili isteğe ulaşabilir, proje revizyonunu 
        gerçekleştirebilirsiniz.""" % self.object.ad, self.object.karar_no)
        sender = self.user
        is_akisini_belli_bir_adimdan_aktif_et(role, self.object, data, step, title, message, sender)

    def ek_butce_talebi_kabul(self):
        """
        Ek bütçe talebinin kabul edilmesi halinde, değişen kalemler güncellenir. 
        Silinecek olan ve yeni eklenen kalemlerin durumları değiştirilir.
        
        """
        ek_butce_bilgileri = json.loads(self.object.gundem_ekstra_bilgiler)
        for kalem_id, data in ek_butce_bilgileri['ek_butce'].items():
            if data['durum'] == 4:
                continue
            kalem = BAPButcePlani.objects.get(kalem_id)
            if data['durum'] == 3:
                kalem.birim_fiyat = data['yeni_birim_fiyat']
                kalem.toplam_fiyat = data['yeni_toplam_fiyat']
                kalem.adet = data['yeni_adet']
                kalem.gerekce = data['gerekce']
                kalem.muhasebe_kod_genel = data['muhasebe_kod_genel']

            kalem.proje_durum = 2 if data['durum'] == 1 else 4
            kalem.save()

        genel = BAPGenel.get()
        mevcut_taahhut_farki = ek_butce_bilgileri['toplam'] - ek_butce_bilgileri['mevcut_toplam']
        genel.toplam_taahhut += mevcut_taahhut_farki
        genel.save()

        eylem = "Ek Bütçe Talebi Kabulü"
        aciklama = "Ek bütçe talebi komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz ek bütçe talebi %s karar numarası ile "
            u"komisyon tarafından onaylanmıştır.") % self.object.proje.ad

        self.bildirim_gonder(bildirim)

    def ek_butce_talebi_red(self):
        """
        Ek bütçe talebinin reddi halinde, değişen kalemler güncellenir. 
        Silinecek olan ve yeni eklenen kalemlerin durumları değiştirilir.

        """
        yeni_kalemler = BAPButcePlani.objects.filter(ilgili_proje=self.object.proje, proje_durum=1)
        self.butce_kalemleri_durum_degistir(durum=3, kalemler=yeni_kalemler)

        eylem = "Ek Bütçe Talebi Reddi"
        aciklama = "Ek bütçe talebi komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz ek bütçe talebi %s karar numarası ile "
            u"komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def fasil_aktarim_talebi_kabul(self):
        """
        Öğretim üyesinin fasıl aktarım talebi kabul edildiğinde, değişiklik yapılan bütçe kalemleri 
        güncellenir. Proje işlem geçmişi güncellenir. 
        
        """
        fasil_bilgileri = json.loads(self.object.gundem_ekstra_bilgiler)
        for kalem_id, data in fasil_bilgileri['fasil_islemleri'].items():
            if data['durum'] == 2:
                continue
            else:
                kalem = BAPButcePlani.objects.get(kalem_id)
                kalem.birim_fiyat = data['yeni_birim_fiyat']
                kalem.toplam_fiyat = data['yeni_toplam_fiyat']
                kalem.adet = data['yeni_adet']
                kalem.gerekce = data['gerekce']
                kalem.muhasebe_kod_genel = data['muhasebe_kod_genel']
                kalem.save()

        genel = BAPGenel.get()
        mevcut_taahhut_farki = fasil_bilgileri['yeni_toplam'] - fasil_bilgileri['mevcut_toplam']
        genel.toplam_taahhut += mevcut_taahhut_farki
        genel.save()

        eylem = "Fasıl Aktarım Talebi Kabulü"
        aciklama = "Fasıl aktarımı talebi komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz fasıl aktarımı talebi %s karar numarası ile "
            u"komisyon tarafından kabul edilmiştir.") % (self.object.proje.ad, self.object.karar_no)

        self.bildirim_gonder(bildirim)

    def fasil_aktarim_talebi_red(self):
        """
        Fasıl aktarımı talebi reddedildiğinde proje geçmişi 
        güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.
        
        """
        eylem = "Fasıl Aktarım Talebi Reddi"
        aciklama = "Fasıl aktarımı talebi komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz fasıl aktarımı talebi %s karar numarası ile "
            u"komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def ek_sure_talebi_kabul(self):
        """
        Ek süre talebi kabul edildiğinde projenin süresi talep edilen ek süre eklenerek 
        güncellenir. Proje geçmişi güncellenir, iilgili öğretim üyesi bilgilendirilir.
        
        """
        ek_sure_bilgileri = json.loads(self.object.gundem_ekstra_bilgiler)
        self.object.proje.sure += int(ek_sure_bilgileri['ek_sure'])
        self.object.proje.save()

        eylem = 'Ek Süre Talebi Kabul'
        aciklama = ', '.join(
            ["Ek süre talebi komisyon tarafından {} karar numarası ile kabul edildi.",
             ek_sure_bilgileri['aciklama']])
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"{} adlı projeniz için yapmış olduğunuz ek süre talebi {} karar numarası ile "
            u"komisyon tarafından kabul edilmiştir.".format(self.object.proje.ad,
                                                            self.object.karar_no))

        self.bildirim_gonder(bildirim)

    def ek_sure_talebi_red(self):
        """
        Ek süre talebi reddedildiğinde proje geçmişi 
        güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        eylem = 'Ek Süre Talebi Red'
        aciklama = "Ek süre talebi komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz ek süre talebi %s karar numarası ile "
            u"komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def proje_sonuc_raporu_basarili(self):
        """
        Proje sonuç raporu kabul edildiğinde, proje raporunun durumu değiştirilir.
        Proje geçmişi güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        self.rapor_durum_degistir(2)
        eylem = 'Proje Sonuç Raporu Kabulü'
        aciklama = "Sonuç raporu komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için sunduğunuz sonuç raporu %s karar numarası ile "
            u"komisyon tarafından kabul edilmiştir.") % (self.object.proje.ad, self.object.karar_no)

        self.bildirim_gonder(bildirim)

    def proje_sonuc_raporu_basarisiz(self):
        """
        Proje sonuç raporu reddedildiğinde, proje raporunun durumu değiştirilir.
        Proje geçmişi güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        self.rapor_durum_degistir(3)
        eylem = 'Proje Sonuç Raporu Reddi'
        aciklama = "Sonuç raporu komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için sunduğunuz sonuç raporu %s karar numarası ile "
            u"komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)
        self.bildirim_gonder(bildirim)

    def proje_donem_raporu_basarili(self):
        """
        Proje dönem raporu kabul edildiğinde, proje raporunun durumu değiştirilir.
        Proje geçmişi güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        self.rapor_durum_degistir(2)
        eylem = 'Proje Dönem Raporu Kabulü'
        aciklama = "Dönem raporu komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için sunduğunuz dönem raporu %s karar numarası ile komisyon "
            u"tarafından kabul edilmiştir.") % (self.object.proje.ad, self.object.karar_no)
        self.bildirim_gonder(bildirim)

    def proje_donem_raporu_basarisiz(self):
        """
        Proje dönem raporu reddedildiğinde, proje raporunun durumu değiştirilir.
        Proje geçmişi güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        self.rapor_durum_degistir(3)
        eylem = 'Proje Dönem Raporu Reddi'
        aciklama = "Dönem raporu komisyon tarafından {} karar numarası ile rededildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için sunduğunuz dönem raporu %s karar numarası ile "
            u"komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)
        self.bildirim_gonder(bildirim)

    def proje_iptal_talebi_kabul(self):
        """
        Öğretim üyesinin proje iptal talebinin kabulünde, projenin durumu iptal anlamına gelen 
        8 yapılır. Projeye ait onaylanmış bütçe kalemlerinin durumu iptal edildi anlamına gelen 
        4 yapılır. Proje ile ilgili olan teklife açık satın alma duyurularının durumu iptal 
        anlamına gelen 4 yapılır.
        
        """
        mevcut_butce = BAPButcePlani.mevcut_butce(proje=self.object.proje)
        genel = BAPGenel.get()
        genel.toplam_taahhut += mevcut_butce
        genel.save()

        eylem = "İptal Talebi Kabulü"
        aciklama = "Projenin iptal talebi komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama, durum=8)
        self.butce_kalemleri_durum_degistir(4)

        for duyuru in BAPSatinAlma.objects.filter(ilgili_proje=self.object.proje, teklif_durum=1):
            duyuru.teklif_durum = 4
            duyuru.save()

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz iptal talebi %s karar numarası ile komisyon "
            u"tarafından kabul edilmiştir.") % (self.object.proje.ad, self.object.karar_no)

        self.bildirim_gonder(bildirim)

    def proje_iptal_talebi_red(self):
        """
        Öğretim üyesinin proje iptal talebinin reddinde, projenin işlem geçmişi güncellenir.
        Öğretim üyesi bilgilendirilir.

        """
        eylem = "İptal Talebi Reddi"
        aciklama = "Projenin iptal talebi komisyon tarafından {} karar numarası ile reddedildi"
        self.islem_gecmisi_guncelle(eylem, aciklama)

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz iptal talebi %s karar numarası ile komisyon "
            u"tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def yurutucu_degisikligi_kabul(self):
        """
        Yürütücü değişikliği kabulünde, projenin yürütücüsü, talep edilen 
        öğretim üyesi ile güncellenir. Proje işlem geçmişi güncellenir, 
        talep eden öğretim üyesine bildirim gönderilir.
        
        """
        yurutucu_bilgileri = json.loads(self.object.gundem_ekstra_bilgiler)
        yeni_yurutucu_id = yurutucu_bilgileri['yeni_yurutucu_id']
        yeni_yurutucu = Okutman.objects.get(yeni_yurutucu_id)

        self.object.proje.yurutucu = yeni_yurutucu
        self.object.proje.yurutucu.save()

        eylem = "Yürütücü Değişikliği Talebi Kabulü"
        aciklama = "Yürütücü değişikliği talebi komisyon " \
                   "tarafından {} karar numarası ile kabul edildi"
        self.islem_gecmisi_guncelle(eylem, aciklama)

        eski_yurutucu_bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz yürütücü değişikliği talebi %s karar numarası "
            u"ile komisyon tarafından kabul edilmiştir. Yeni yürütücü: %s") % (
                                     self.object.proje.ad, self.object.karar_no,
                                     yeni_yurutucu.__unicode__)
        self.bildirim_gonder(eski_yurutucu_bildirim)

        yeni_yurutucu_bildirim = _(
            u"%s karar numarası ile %s adlı projenin yeni yürütücüsü olmanız komisyon tarafından "
            u"onay verilmiştir.") % (
                                     self.object.proje.ad,
                                     self.object.karar_no,
                                     yeni_yurutucu.__unicode__)

        yeni_yurutucu.personel.user.send_notification(title='Komisyon Kararı',
                                                      message=yeni_yurutucu_bildirim,
                                                      sender=self.user)

    def yurutucu_degisikligi_red(self):
        """
        Yürütücü değişikliği reddinde proje işlem geçmişi güncellenir,
        talep eden öğretim üyesine bildirim gönderilir.

        """
        eylem = "Yürütücü Değişikliği Talebi Reddi"
        aciklama = "Yürütücü değişikliği talebi komisyon tarafından {} karar numarası ile reddedildi"
        self.islem_gecmisi_guncelle(eylem, aciklama)

        bildirim = _(
            u"%s adlı projeniz için yapmış olduğunuz yürütücü değişikliği talebi %s karar numarası "
            u"ile komisyon tarafından reddedilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)

        self.bildirim_gonder(bildirim)

    def etkinlik_basvuru_kabul(self):
        """
        Etkinlik başvuru kabulünde başvuru yapan öğretim üyesine bildirim gönderilir. Durumu 
        onaylandı anlamına gelen 2 yapılır.

        """
        self.object.etkinlik.durum = 2
        self.object.save()

        bildirim = _(
            u"Yapmış olduğunuz etkinlik başvurusu talebi %s karar numarası "
            u"ile komisyon tarafından kabul edilmiştir.") % (self.object.karar_no)

        self.object.etkinlik.basvuru_yapan.personel.user.send_notification(
            title="Etkinlik Başvurusu Komisyon Kararı",
            message=bildirim)

    def etkinlik_basvuru_red(self):
        """
        Etkinlik başvuru kabulünde başvuru yapan öğretim üyesine bildirim gönderilir. Durumu 
        reddedildi anlamına gelen 3 yapılır.
        
        """
        self.object.etkinlik.durum = 3
        self.object.save()
        bildirim = _(
            u"Yapmış olduğunuz etkinlik başvurusu talebi %s karar numarası "
            u"ile komisyon tarafından reddedilmiştir. Gerekçe: %s") % (self.object.karar_no,
                                                                       self.object.karar_gerekcesi)
        self.object.etkinlik.basvuru_yapan.personel.user.send_notification(
            title="Etkinlik Başvurusu Komisyon Kararı",
            message=bildirim)

    def islem_gecmisi_guncelle(self, eylem, aciklama, durum=None):
        """
        Gönderilen eylem ve açıklama ile, seçilmiş gündemin projesinin işlem geçmişini günceller.
        
        Args:
            eylem(str): İşlem ana başlığı 
            aciklama(str): İşlemin içeriği

        """

        self.object.proje.ProjeIslemGecmisi(aciklama=aciklama.format(self.object.karar_no),
                                            eylem=eylem, tarih=datetime.now())
        if durum:
            self.object.proje.durum = durum
        self.object.proje.save()

    def bildirim_gonder(self, bildirim, role=None):
        """
        Gönderilen bildirim mesajı ile, seçilmiş gündemin projesinin yürütücüsüne bildirim gönderir.
        
        Args:
            bildirim(str): Gönderilecek bildirim mesajı. 

        """
        role = role or self.object.proje.basvuru_rolu
        role.send_notification(
            title=_(u"Komisyon Kararı"),
            message=bildirim,
            sender=self.user)

    def butce_kalemleri_durum_degistir(self, durum, kalemler=None):
        """
        Eğer var ise değişiklik istenen kalemler ile yoksa default olarak 
        gündemin projesinin bütçe kalemleri istenen durum ile değiştirilir.
        
        Args:
            durum(int): Kalemlerin durumu (1: Onaylandi, 2: Reddedildi gibi.) 
            kalemler(list): durumu değiştirilmesi istenen kalemler. 

        """
        kalemler = kalemler or BAPButcePlani.objects.filter(ilgili_proje=self.object.proje)
        for kalem in kalemler:
            kalem.proje_durum = durum
            kalem.save()

    def rapor_durum_degistir(self, durum):
        """
        Gönderilen durum ile raporun durumu güncellenir.
        
        Args:
            durum(int): Raporun durumu 

        """
        rapor_id = json.loads(self.object.gundem_ekstra_bilgiler).get('rapor')
        rapor = BAPRapor.objects.get(rapor_id)
        rapor.durum = durum
        rapor.save()

    def butce_fisi_is_akisini_tetikle(self):
        """
        Projenin kabulü sonrası, bütçe fişi iş akışını çalıştırma izini olan personele davet 
        yollanır.
                
        """
        wf = BPMNWorkflow.objects.get(name='bap_butce_fisi')
        perm = Permission.objects.get('bap_butce_fisi')
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        today = datetime.today()
        for role in perm.get_permitted_roles():
            wfi = WFInstance(
                wf=wf,
                current_actor=role,
                task=None,
                name=wf.name,
                wf_object=self.object.proje.key
            )
            wfi.data = {'bap_proje_id': self.object.proje.key}
            wfi.pool = {}
            wfi.blocking_save()
            role.send_notification(title=_(u"{} | {} | Bütçe Fişi İş Akışı".format(
                self.object.proje.yurutucu.__unicode__(),
                self.object.proje.ad)),
                message=_(u"""{} adlı onaylanmış projenin bütçe fişi kesilmesi gerekmektedir. 
                        Görev yöneticinizden ilgili isteğe ulaşabilir, 
                        iş akışını çalıştırabilirsiniz.""".format(self.object.ad)),
                typ=1,
                sender=sistem_user
            )
            inv = TaskInvitation(
                instance=wfi,
                role=role,
                wf_name=wfi.wf.name,
                progress=30,
                start_date=today,
                finish_date=today + timedelta(15)
            )
            inv.title = _(u"{} | {} | Bütçe Fişi İş Akışı".format(
                self.object.proje.yurutucu.__unicode__(),
                self.object.proje.ad))
            inv.save()
