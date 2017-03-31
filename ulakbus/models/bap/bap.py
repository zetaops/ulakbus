# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field, ListNode
from zengine.lib.translation import gettext_lazy as __, gettext as _
from ulakbus.models.form import Form
from ulakbus.models import Room, Personel
from ulakbus.models.demirbas import Demirbas
from ulakbus.models.akademik_faaliyet import AkademikFaaliyet
from pyoko.lib.utils import lazy_property
import datetime


class BAPProjeTurleri(Model):
    kod = field.String(__(u"Proje tür kodu"))
    ad = field.String(__(u"Proje türünün Adı"))
    aciklama = field.Text(__(u"Proje türüne dair açıklama"))
    min_sure = field.Integer(__(u"Projenin minumum süreceği ay sayısı"))
    max_sure = field.Integer(__(u"Projenin maximum süreceği ay sayısı"))
    butce_ust_limit = field.Float(__(u"Projenin üst limiti"))

    class Meta:
        app = 'Proje Türleri'
        verbose_name = __(u"Proje Türü")
        verbose_name_plural = __(u"Proje Türleri")
        list_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']
        search_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']

    class Belgeler(ListNode):
        class Meta:
            verbose_name = __(U"Projede Kullanılacak Belge")
            verbose_name_plural = __(u"Projede Kullanılacak Belgeler")

        ad = field.String(__(u"Belgenin İsmi"))
        gereklilik = field.Boolean(__(u"Belgenin Gerekliliği"))

    class Formlar(ListNode):
        class Meta:
            verbose_name = __(u"Projede Kullanılacak Form")
            verbose_name_plural = __(u"Projede Kullanılacak Formlar")

        proje_formu = Form()
        gereklilik = field.Boolean(__(u"Formun Gerekliliği"))

    def __unicode__(self):
        return "%s: %s" % (self.kod, self.ad)


class BAPProje(Model):

    # Komisyon kararıyla doldurulacak alanlar
    proje_no = field.String(_(u"Proje No"))
    kabul_edilen_baslama_tarihi = field.Date(_(u"Kabul Edilen Başlama Tarihi"))
    kabul_edilen_butce = field.Float(_(u"Kabul Edilen Bütçe"))

    # Başvuruda doldurulacak alanlar
    yurutucu = Personel()
    tur = BAPProjeTurleri()
    # ay
    sure = field.Integer(_(u"Süre"))
    anahtar_kelimeler = field.String(_(u"Anahtar Kelimeler"))
    teklif_edilen_baslama_tarihi = field.Date(_(u"Teklif Edilen Başlama Tarihi"))
    teklif_edilen_butce = field.Float(_(u"Teklif Edilen Bütçe"))
    konu_ve_kapsam = field.Text(_(u"Konu ve Kapsam"))
    literatur_ozeti = field.Text(_(u"Literatür Özeti"))
    ozgun_deger = field.Text(_(u"Özgün Değer"))
    hedef_ve_amac = field.Text(_(u"Hedef ve Amaç"))
    yontem = field.Text(_(u"Yöntem"))
    basari_olcutleri = field.Text(_(u"Başarı Ölçütleri"))
    b_plani = field.Text(_(u"B Planı"))

    class ArastirmaOlanaklari(ListNode):
        class Meta:
            verbose_name = __(u"Araştırma Olanağı")
            verbose_name_plural = __(u"Araştırma Olanakları")

        lab = Room()
        demirbas = Demirbas()
        personel = Personel()

    class ProjeCalisanlari(ListNode):
        class Meta:
            verbose_name = __(u"Proje Çalışanı")
            verbose_name_plural = __(u"Proje Çalışanları")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        nitelik = field.String(_(u"Nitelik"))
        calismaya_katkisi = field.String(_(u"Çalışmaya Katkısı"))

    class UniversiteDisiUzmanlar(ListNode):
        class Meta:
            verbose_name = __(u"Üniversite Dışı Uzman")
            verbose_name_plural = __(u"Üniversite Dışı Uzmanlar")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        unvan = field.String(_(u"Unvan"))
        kurum = field.String(_(u"Kurum"))
        tel = field.String(_(u"Telefon"))
        faks = field.String(_(u"Faks"))
        eposta = field.String(_(u"E-posta"))

    class UniversiteDisiDestek(ListNode):
        class Meta:
            verbose_name = __(u"Üniversite Dışı Destek")
            verbose_name_plural = __(u"Üniversite Dışı Destekler")

        kurulus = field.String(_(u"Destekleyen Kurulus"))
        tur = field.String(_(u"Destek Türü"))
        destek_miktari = field.String(_(u"Destek Miktarı"))
        verildigi_tarih = field.Date(_(u"Verildiği Tarih"))
        # ay
        sure = field.Integer(_(u"Süresi"))
        destek_belgesi = field.String(_(u"Destek Belgesi"))

    class BAPHakem(ListNode):
        class Meta:
            verbose_name = __(u"Hakem")
            verbose_name_plural = __(u"Hakemler")

        ad = field.String(_(u"Ad"))
        soyad = field.String(_(u"Soyad"))
        birim = field.String(_(u"Birim"))

    # Proje Yürütücüsü Tecrübesi
    @lazy_property
    def yurutucu_tecrubesi(self):
        simdiki_tarih = datetime.date.today()
        faaliyetler = AkademikFaaliyet.objects.filter(
            baslama__lte=simdiki_tarih,
            bitis__gte=simdiki_tarih,
            personel=self.yurutucu
        )
        return faaliyetler if faaliyetler else None

    @lazy_property
    def yurutucu_diger_projeler(self):
        return self.objects.filter(yurutucu=self.yurutucu)
