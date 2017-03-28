# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import Model, field
from ulakbus.models import Personel, Unit
from ulakbus.settings import DATE_DEFAULT_FORMAT
from zengine.lib.translation import gettext as _


class Demirbas(Model):
    ad = field.String(_(u"Adı"))
    tur = field.String(_(u"Türü"))
    url = field.String(_(u"Url"))
    olculer = field.String(_(u"Ölçüler"))
    yeri = field.String(_(u"Yeri"))
    muhasebe_kodu = field.String(_(u"Muhasebe Kodu"))
    kurum_kodu = field.String(_(u"Kurum Kodu"))

    demirbas_no = field.String(_(u"Demirbas Numarası"))
    # satin_alindigi_proje = Proje()
    satin_alinma_tarihi = field.Date(_(u"Satın Alınma Tarihi"), format=DATE_DEFAULT_FORMAT)
    teslim_alinma_tarihi = field.Date(_(u"Teslim Alınma Tarihi"), format=DATE_DEFAULT_FORMAT)
    satin_alinma_fiyati = field.Float(_(u"Maliyet"))
    # teknik özellikler = ???
    etiketler = []
    marka = field.String(_(u"Marka"))
    model = field.String(_(u"Model"))
    # durum = Uygun, Kullanımda
    birim = Unit(_(u"Birim"))
    notlar = field.Text(_(u"Notlar"))

    class Meta:
        app = 'Demirbas'
        verbose_name = _(u"Demirbaş")
        verbose_name_plural = _(u"Demirbaşlar")
        list_fields = ['ad', 'tur', 'demirbas_no', 'satin_alinma_tarihi', 'teslim_alinma_tarihi']
        search_fields = ['ad', 'tur', 'demirbas_no', 'tckn', 'marka', 'model']

    def __unicode__(self):
        return _(u"%(ad)s %(tur)s") % {'ad': self.ad, 'tur': self.tur}


class DemirbasRezervasyon(Model):
    rezerve_eden = Personel()
    rezervasyon_baslama_tarihi = field.Date(_(u"Rezervasyon Başlama Tarihi"),
                                            format=DATE_DEFAULT_FORMAT)
    rezervasyon_bitis_tarihi = field.Date(_(u"Rezervasyon Başlama Tarihi"),
                                          format=DATE_DEFAULT_FORMAT)
    rezerve_edilen_demirbas = Demirbas()

    # proje = Proje()

    class Meta:
        app = 'RezerveBilgileri'
        verbose_name = _(u"RezerveBilgileri")
        verbose_name_plural = _(u"RezerveBilgileri")
        list_fields = ['rezerve_eden', 'rezervasyon_baslama_tarihi', 'rezervasyon_bitis_tarihi']
        search_fields = ['rezerve_eden', 'rezervasyon_baslama_tarihi', 'rezervasyon_bitis_tarihi']






