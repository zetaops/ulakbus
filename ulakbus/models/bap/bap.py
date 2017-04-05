# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models.form import Form

from zengine.lib.translation import gettext_lazy as __

from pyoko import Model, field, ListNode


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
        gereklilik = field.Boolean(__(u"Belgenin Gerekliliği"))

    class Formlar(ListNode):
        class Meta:
            verbose_name = __(u"Projede Kullanılacak Form")
            verbose_name_plural = __(u"Projede Kullanılacak Formlar")

        proje_formu = Form()
        gereklilik = field.Boolean(__(u"Formun Gerekliliği"))

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

        proje_turu = BAPProjeTurleri()

    class OnemliTarihler(ListNode):
        class Meta:
            verbose_name = __(u"Önemli Tarih")
            verbose_name_plural = __(u"Önemli Tarihler")

        baslangic_tarihi = field.Date(__(u"Başlangıç Tarihi"))
        bitis_tarihi = field.Date(__(u"Bitiş Tarihi"))
        aciklama = field.Integer(__(u"Açıklama Seçiniz"), choices='onemli_tarih_aciklama')

    takvim_aciklama = field.Text(__(u"Takvim Açıklaması"))
    donem = field.Integer(__(u"Takvimin Yayınlanacağı Dönem"))

    def __unicode__(self):
        return "%s. Dönem: %s" % (self.donem, self.takvim_aciklama)

    def _takvim_turu(self):
        if self.ProjeTuru:
            return ''.join(["""
            %s\n""" % proje.proje_turu.ad for proje in self.ProjeTuru])
        else:
            return """
            Genel Takvim"""

    def _tarih(self):
        return ''.join(["""
        %s - %s\n""" % (tarih.baslangic_tarihi, tarih.bitis_tarihi) for tarih in
                        self.OnemliTarihler])

    _takvim_turu.title = __(u"Takvim Türü")
    _tarih.title = __(u"Tarih")
