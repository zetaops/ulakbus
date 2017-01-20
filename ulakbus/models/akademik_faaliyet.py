# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import Model
from pyoko.fields import Integer, String, Date
from zengine.lib.translation import gettext as _
from zengine.lib.translation import gettext_lazy as __
from ulakbus.models import Personel

__author__ = 'Ali Riza Keles'


class AkademikFaaliyetTuru(Model):
    faaliyet = String("Faaliyet")
    puan = Integer("Puan")
    alt_faaliyet = String("Alt Faaliyet")
    detay = String("Detay")
    oran = Integer("Oran")

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Akademik Faaliyet Türü")
        verbose_name_plural = _(u"Akademik Faaliyet Türleri")
        list_fields = ['faaliyet', 'puan', 'alt_faaliyet', 'detay', 'oran']
        search_fields = ['faaliyet', 'alt_faaliyet', 'detay']

    def __unicode__(self):
        return _(u"%(faaliyet)s | %(detay)s") % {'faaliyet': self.faaliyet,
                                                        'detay': self.detay}

    @classmethod
    def get_alt_faaliyet_by_faaliyet(cls, faaliyet):
        return cls.objects.filter(faaliyet=faaliyet).values('key', 'alt_faaliyet')

    @classmethod
    def get_faaliyet_list(cls, faaliyet):
        return cls.objects.distinct_values_of('faaliyet').values('key', 'alt_faaliyet')


class AkademikFaaliyet(Model):
    """
    Akademik Faalyet bilgilerinin saklandigi model
    """
    tur = AkademikFaaliyetTuru(__(u"Faaliyet Tipi"))
    ad = String(__(u"Faaliyet Adı"))
    baslama = Date(__(u"Başlama Tarihi"), format="%d.%m.%Y")
    bitis = Date(__(u"Bitiş Tarihi"), format="%d.%m.%Y")
    durum = Integer(__(u"Durum"), choices='akademik_faaliyet_durum', required=False, default=1)
    kac_kisiyle_yapildi = Integer(__(u"Kaç kişiyle yapıldığı"), required=False)
    gorev = String(__(u"Görev"), required=False)
    personel = Personel()

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Akademik Faaliyet")
        verbose_name_plural = _(u"Akademik Faaliyetler")
        list_fields = ['ad', 'baslama', 'bitis', 'durum']
        search_fields = ['ad', ]

    def __unicode__(self):
        return _(u"%(ad)s %(tur)s") % {'ad': self.ad, 'tur': self.tur}
