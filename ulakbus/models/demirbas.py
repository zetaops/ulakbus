# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import Model, field
from ulakbus.models import Personel, Unit
from ulakbus.settings import DATE_DEFAULT_FORMAT
from zengine.lib.translation import gettext as _
from datetime import datetime


class Demirbas(Model):
    ad = field.String(_(u"Adı"))
    tur = field.String(_(u"Türü"), required=False)
    url = field.String(_(u"Url"), required=False)
    olculer = field.String(_(u"Ölçüler"), required=False)
    yeri = field.String(_(u"Yeri"), required=False)
    muhasebe_kodu = field.String(_(u"Muhasebe Kodu"), required=False)
    kurum_kodu = field.String(_(u"Kurum Kodu"), required=False)

    demirbas_no = field.String(_(u"Demirbas Numarası"))
    satin_alindigi_proje = field.String(_(u"Satın Alındığı Proje"), required=False)
    satin_alinma_tarihi = field.Date(_(u"Satın Alınma Tarihi"))
    teslim_alinma_tarihi = field.Date(_(u"Teslim Alınma Tarihi"))
    satin_alinma_fiyati = field.Float(_(u"Maliyet"))
    teknik_ozellikler = field.Text(_(u"Teknik Özellikler"), required=False)

    # virgülle ayrılacak
    etiketler = field.String(_(u"Etiketler"), required=False)
    marka = field.String(_(u"Marka"), required=False)
    model = field.String(_(u"Model"), required=False)
    durum = field.Integer(_(u"Durum"), choices='demirbas_durum')
    birim = Unit(_(u"Birim"), required=False)
    sorumlu = Personel()
    notlar = field.Text(_(u"Notlar"), required=False)

    class Meta:
        app = 'Genel'
        verbose_name = _(u"Demirbaş")
        verbose_name_plural = _(u"Demirbaşlar")
        list_fields = ['ad', 'tur', 'demirbas_no', 'satin_alinma_tarihi', 'teslim_alinma_tarihi',
                       'rezervasyonlar']
        search_fields = ['ad', 'tur', 'etiketler', 'marka', 'model', 'demirbas_no']

    def __unicode__(self):
        return _(u"%(ad)s") % {'ad': self.ad}

    def rezervasyonlar(self):
        rezervasyonlar = DemirbasRezervasyon.objects.filter(
            rezerve_edilen_demirbas_id=self.key)

        onceki_rezervasyonlar = []

        simdi = datetime.now().date()

        if not rezervasyonlar:
            onceki_rezervasyonlar.append(_(u"Bu demirbaşa ait rezervasyon bulunmamaktadır."))
        else:
            for rez in rezervasyonlar:
                onceki_rezervasyonlar.append("(%s - %s) - %s" % (
                    datetime.strftime(rez.rezervasyon_baslama_tarihi, DATE_DEFAULT_FORMAT),
                    datetime.strftime(rez.rezervasyon_bitis_tarihi, DATE_DEFAULT_FORMAT),
                    rez.rezerve_eden))
                if rez.rezervasyon_baslama_tarihi < simdi < rez.rezervasyon_bitis_tarihi:
                    self.durum = 2
                    self.blocking_save()
        return "\n".join(onceki_rezervasyonlar) if len(onceki_rezervasyonlar) > 1 else \
            onceki_rezervasyonlar[0]

    rezervasyonlar.title = _(u"Rezervasyonlar")


class DemirbasRezervasyon(Model):
    rezerve_eden = Personel()
    rezervasyon_baslama_tarihi = field.Date(_(u"Rezervasyon Başlama Tarihi"),
                                            format=DATE_DEFAULT_FORMAT)
    rezervasyon_bitis_tarihi = field.Date(_(u"Rezervasyon Başlama Tarihi"),
                                          format=DATE_DEFAULT_FORMAT)
    rezerve_edilen_demirbas = Demirbas()

    class Meta:
        app = 'Genel'
        verbose_name = _(u"Rezerve Bilgileri")
        verbose_name_plural = _(u"Rezerve Bilgileri")
        list_fields = ['rezerve_eden', 'rezervasyon_baslama_tarihi', 'rezervasyon_bitis_tarihi']
        search_fields = ['rezerve_eden', 'rezervasyon_baslama_tarihi', 'rezervasyon_bitis_tarihi']






