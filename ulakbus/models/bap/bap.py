# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models.form import Form

from zengine.lib.translation import gettext_lazy as __

from pyoko import Model, field, ListNode


class BAPProje(Model):
    pass


class BAPProjeTurleri(Model):
    kod = field.String(__(u"Proje tür kodu"))
    ad = field.String(__(u"Proje türünün Adı"))
    aciklama = field.Text(__(u"Proje türüne dair açıklama"))
    min_sure = field.Integer(__(u"Projenin minumum süreceği ay sayısı"))
    max_sure = field.Integer(__(u"Projenin maximum süreceği ay sayısı"))
    butce_ust_limit = field.Float(__(u"Projenin üst limiti"))

    class Meta:
        verbose_name = __(u"Proje Türü")
        verbose_name_plural = __(u"Proje Türleri")
        list_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']
        list_filters = ['kod', 'ad']
        search_fields = ['kod', 'ad', 'min_sure', 'max_sure', 'butce_ust_limit']

    class Belgeler(ListNode):
        class Meta:
            verbose_name = __(U"Projede Kullanılacak Belge")
            verbose_name_plural = __(u"Projede Kullanılacak Belgeler")

        ad = field.String(__(u"Belgenin İsmi"))
        gereklilik = field.Boolean(__(u"Belgenin Zorunluluğu"))

    class Formlar(ListNode):
        class Meta:
            verbose_name = __(u"Projede Kullanılacak Form")
            verbose_name_plural = __(u"Projede Kullanılacak Formlar")

        proje_formu = Form()
        gereklilik = field.Boolean(__(u"Formun Gerekliliği"), default=False)
        secili = field.Boolean(__(u"Projeye Dahil Et"), default=False)

    def __unicode__(self):
        return "%s: %s" % (self.kod, self.ad)


class BAPTakvim(Model):
    class Meta:
        search_fields = ['ProjeTuru', 'aciklama', ]
        list_fields = ['donem', '_takvim_turu', '_tarih', 'takvim_aciklama']

    class ProjeTuru(ListNode):
        class Meta:
            verbose_name = __(u"Proje Türü")
            verbose_name_plural = __(u"Proje Türleri")

        proje_turu = field.String(__(u"Proje Türleri"))

    class OnemliTarihler(ListNode):
        class Meta:
            verbose_name = __(u"Önemli Tarih")
            verbose_name_plural = __(u"Önemli Tarihler")

        baslangic_tarihi = field.Date(__(u"Başlangıç Tarihi"))
        bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))
        aciklama = field.Integer(__(u"Açıklama Seçiniz"), choices='onemli_tarih_aciklama',
                                 default=1)

    takvim_aciklama = field.Text(__(u"Takvim Açıklaması"))
    donem = field.Integer(__(u"Takvimin Yayınlanacağı Dönem"))

    def __unicode__(self):
        return "%s. Dönem: %s" % (self.donem, self.takvim_aciklama)

    def _takvim_turu(self):
        if self.ProjeTuru:
            return ''.join(["""
            %s\n""" % proje.proje_turu for proje in self.ProjeTuru])
        else:
            return """
            Genel Takvim"""

    def _tarih(self):
        return ''.join(["""
        %s / %s\n""" % (tarih.baslangic_tarihi.strftime("%d.%m.%Y"),
                        tarih.bitis_tarihi.strftime("%d.%m.%Y")) for tarih in
                        self.OnemliTarihler])

    _takvim_turu.title = __(u"Proje Türü")
    _tarih.title = __(u"Tarih")


class BAPIs(Model):
    class Meta:
        verbose_name = __(u"Bap İş Türü")
        verbose_name_plural = __(u"Bap İş Türleri")

    ad = field.String(__(u"Bap İş"))
    baslama_tarihi = field.Date(__(u"Başlama Tarihi"))
    bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))

    def __unicode__(self):
        return "%s" % self.ad


class BAPIsPaketi(Model):
    class Meta:
        verbose_name = __(u"Bap İş Paketi")
        verbose_name_plural = __(u"Bap İş Paketleri")

    ad = field.String(__(u"İş Paketinin Adı"))
    baslama_tarihi = field.Date(__(u"Başlama Tarihi"))
    bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))

    class Isler(ListNode):
        isler = BAPIs()

    def __unicode__(self):
        return "%s" % self.ad


class BAPButcePlani(Model):
    class Meta:
        verbose_name = __(u"Bap Bütçe Planı")
        verbose_name_plural = __(u"Bap Bütçe Planları")
        list_fields = ['_muhasebe_kod', 'kod_adi', 'ad', 'birim_fiyat', 'adet', 'toplam_fiyat']

    muhasebe_kod = field.String(__(u"Muhasebe Kod"),
                                choices='analitik_butce_dorduncu_duzey_gider_kodlari',
                                default="03.2.6.90")
    kod_adi = field.String(__(u"Kod Adı"))
    ad = field.String(__(u"Alınacak Malzemenin Adı"))
    birim_fiyat = field.Float(__(u"Birim Fiyat"))
    adet = field.Integer(__(u"Adet"))
    toplam_fiyat = field.Float(__(u"Toplam Fiyat"))
    gerekce = field.Text(__(u"Gerekçe"))
    ilgili_proje = field.String(__(u"Bağlı olduğu Projenin Adı"), readonly=True, required=False)
    onay_tarihi = field.Date(__(u"Onay Tarihi"))
    
    def __unicode__(self):
        return "%s / %s / %s" % (self.muhasebe_kod, self.kod_adi, self.ad)

    def _muhasebe_kod(self):
        return self.muhasebe_kod

    _muhasebe_kod.title = __(u"Muhasebe Kodu")
