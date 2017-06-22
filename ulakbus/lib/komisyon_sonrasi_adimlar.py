# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.common import is_akisini_belli_bir_adimdan_aktif_et
from ulakbus.models import BAPButcePlani, BAPRapor, Okutman, Role
from zengine.lib.translation import gettext as _
from datetime import datetime
import json

kalem_degisiklik = {'adet': 'yeni_adet',
                    'birim_fiyat': 'yeni_birim_fiyat',
                    'toplam_fiyat': 'yeni_toplam_fiyat'}


class KomisyonKarariSonrasiAdimlar():
    def __init__(self, obj, user):
        self.object = obj
        self.user = user

    def proje_basvurusu_kabul(self):
        """
        Projenin durumu komisyon tarafından onaylandı anlamına gelen 5 yapılır.
    
        """
        self.object.proje.durum = 5
        self.object.proje.save()
        # bütçe fişi iş akışını tetikle

        eylem = "Onaylandı"
        aciklama = "Proje, komisyon tarafından {} karar numarası ile onaylandı."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        self.butce_kalemleri_durum_degistir(durum=2)

        bildirim = _(
            u"%s adlı projeniz %s karar numarası ile komisyon tarafından onaylanmıştır.") % (
                       self.object.proje.ad, self.object.karar_no)

        self.bildirim_gonder(bildirim)

    def proje_basvurusu_red(self):
        """
        Projenin durumu komisyon tarafından reddedildi anlamına gelen 6 yapılır.

        """
        self.object.proje.durum = 6
        self.object.proje.save()

        eylem = "Reddedildi"
        aciklama = "Proje komisyon tarafından {} karar numarası ile reddedildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
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
        self.object.proje.durum = 7
        self.object.proje.save()

        eylem = "Revizyon"
        aciklama = "Proje, komisyon tarafindan {} karar numarası ile revizyona gonderildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)

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
        for kalem_id, data in ek_butce_bilgileri['degisen_kalemler'].items():
            kalem = BAPButcePlani.objects.get(kalem_id)
            if data['durum'] == 'Silinecek':
                kalem.durum = 3
            elif data['durum'] == 'Düzenlendi':
                for k, v in kalem_degisiklik.items():
                    setattr(kalem, k, data[v])
            else:
                kalem.durum = 2
            kalem.save()

        eylem = "Ek Bütçe Talebi Kabulü"
        aciklama = ' '.join([
            "Ek bütçe talebi komisyon tarafından {} karar numarası ile kabul edildi.",
            ek_butce_bilgileri['degisen_kalemler_aciklama']])
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
        yeni_kalemler = BAPButcePlani.objects.filter(ilgili_proje=self.object.proje, durum=1)
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
        for kalem_id, data in fasil_bilgileri['degisen_kalemler'].items():
            kalem = BAPButcePlani.objects.get(kalem_id)
            for k, v in kalem_degisiklik.items():
                setattr(kalem, k, data[v])
            kalem.save()

        eylem = "Fasıl Aktarım Talebi Kabulü"
        aciklama = ' '.join([
            "Fasıl aktarımı talebi komisyon tarafından {} karar numarası ile kabul edildi.",
            fasil_bilgileri['degisen_kalemler_aciklama']])
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
            u"%s adlı projeniz için yapmış olduğunuz ek süre talebi %s karar numarası ile "
            u"komisyon tarafından kabul edilmiştir.") % (self.object.proje.ad, self.object.karar_no)

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

    def proje_sonuc_raporu_kabul(self):
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

    def proje_sonuc_raporu_red(self):
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

    def proje_sonuc_raporu_revizyon(self):
        """
        Proje sonuç raporu kabul edildiğinde, proje raporunun durumu değiştirilir.
        Proje geçmişi güncellenir ve öğretim üyesi karar hakkında bilgilendirilir.

        """
        self.rapor_durum_degistir(4)
        eylem = 'Proje Sonuç Raporu Kabulü'
        aciklama = "Sonuç raporu komisyon tarafından {} karar numarası ile revizyona gonderildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(
            u"%s adlı projeniz için sunduğunuz sonuç raporu %s karar numarası ile "
            u"komisyon tarafından revizyona gonderilmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)
        self.bildirim_gonder(bildirim)

    def proje_donem_raporu_kabul(self):
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

    def proje_donem_raporu_red(self):
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

    def proje_donem_raporu_revizyon(self):
        self.rapor_durum_degistir(4)
        eylem = 'Proje Dönem Raporu Revizyonu'
        aciklama = "Dönem raporu için komisyon tarafından {} karar numarası ile revizyon istendi."
        self.islem_gecmisi_guncelle(eylem, aciklama)
        bildirim = _(u"%s adlı projeniz için sunduğunuz dönem raporu için %s karar numarası ile "
                     u"komisyon tarafından revizyon istenmiştir. Gerekçe: %s") % (
                       self.object.proje.ad, self.object.karar_no, self.object.karar_gerekcesi)
        self.bildirim_gonder(bildirim)

    def proje_iptal_talebi_kabul(self):
        """
        Öğretim üyesinin proje iptal talebinin kabulünde, projenin durumu iptal anlamına gelen 8 
        yapılır. Projeye ait onaylanmış bütçe kalemlerinin durumu geçersiz anlamına gelen 3 yapılır.
        
        """
        eylem = "İptal Talebi Kabulü"
        aciklama = "Projenin iptal talebi komisyon tarafından {} karar numarası ile kabul edildi."
        self.islem_gecmisi_guncelle(eylem, aciklama)

        self.object.proje.durum = 8
        self.object.proje.save()

        self.butce_kalemleri_durum_degistir(3)

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
        Yürütücü değişikliği kabulünde, projenin yürütücüsü, talep edilen öğretim üyesi ile 
        güncellenir. Proje işlem geçmişi güncellenir, talep eden öğretim üyesine bildirim gönderilir.
        
        """
        yurutucu_bilgileri = json.loads(self.object.gundem_ekstra_bilgiler)
        yeni_yurutucu_id = yurutucu_bilgileri['yurutucu_id']
        yeni_yurutucu_role_id = yurutucu_bilgileri['role_id']
        yeni_yurutucu = Okutman.objects.get(yeni_yurutucu_id)
        yeni_yurutucu_role = Role.objects.get(yeni_yurutucu_role_id)

        self.object.proje.yurutucu = yeni_yurutucu
        self.object.proje.yurutucu.save()

        eylem = "Yürütücü Değişikliği Talebi Kabulü"
        aciklama = "Yürütücü değişikliği talebi komisyon tarafından {} karar numarası ile kabul edildi"
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
                                     self.object.proje.ad, self.object.karar_no,
                                     yeni_yurutucu.__unicode__)
        self.bildirim_gonder(yeni_yurutucu_bildirim, role=yeni_yurutucu_role)

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

    def islem_gecmisi_guncelle(self, eylem, aciklama):
        """
        Gönderilen eylem ve açıklama ile, seçilmiş gündemin projesinin işlem geçmişini günceller.
        
        Args:
            eylem(str): İşlem ana başlığı 
            aciklama(str): İşlemin içeriği

        """
        self.object.proje.ProjeIslemGecmisi(aciklama=aciklama.format(self.object.karar_no),
                                            eylem=eylem, tarih=datetime.now())
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
            kalem.durum = durum
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
