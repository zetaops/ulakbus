# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Bina ve Oda Modülü

Bu modül Ulakbus uygulaması için üniversite yerleşim modellerini içerir. Modellerin
amacı Üniversitelere ait yerleşke, bina ve oda bilgilerinin ilişkileri ile birlikte saklanmasıdır.

Campus, Building, RoomType, Room ve RoomFeature modellerinden oluşur.

"""

from pyoko import field, Model, ListNode
from zengine.lib.translation import gettext_lazy as _
from ulakbus.models import Unit

__author__ = 'Ali Riza Keles'


class Campus(Model):
    """Kampüs Modeli

    Üniversite kampüslerine ait data modeli. Kampus adı ve koordinat bilgilerini içerir.

    Kampüs koordinatları lokasyon bazlı hesaplamalar için kullanılacaktır. Özellikle
    Unitime ile ders programı hazırlarken farklı lokasyonlar arası zaman hesaplamalarında
    kullanılmaktadır.

    """

    code = field.String(_(u"Kod"), index=True)
    name = field.String(_(u"İsim"), index=True)
    coordinate_x = field.String(_(u"X Koordinatı"), index=True)
    coordinate_y = field.String(_(u"Y Koordinatı"), index=True)

    class Meta:
        verbose_name = _(u"Yerleşke")
        verbose_name_plural = _(u"Yerleşkeler")
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.coordinates())

    def coordinates(self):
        """Koordinatlar

        Returns:
            x ve y koordinatlarını birlikte döndürür.

        """
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class Building(Model):
    """Bina Modeli

    Universite kampuslerindeki binalara ait data modeli. Bina kod ve adının yanısıra
    koordinat bilgilerini içerir.

    Bina koordinatları lokasyon bazlı hesaplamalar için kullanılacaktır. Özellikle
    Unitime ile ders programı hazırlarken farklı lokasyonlar arası zaman hesaplamalarında
    kullanılmaktadır.

    """

    code = field.String(_(u"Kod"), index=True)
    name = field.String(_(u"İsim"), index=True)
    coordinate_x = field.String(_(u"X Koordinatı"), index=True)
    coordinate_y = field.String(_(u"Y Koordinatı"), index=True)
    campus = Campus()

    class Meta:
        verbose_name = _(u"Bina")
        verbose_name_plural = _(u"Binalar")
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s %s' % (self.code, self.name, self.coordinates(), self.campus)

    def coordinates(self):
        """"Koordinatlar

        Returns:
            x ve y koordınatlarını birlikte döndürür.
        """
        return '%s %s' % (self.coordinate_x, self.coordinate_y)


class RoomType(Model):
    """Oda tipleri modeli

    Odalar sinif, amfi, salon, kimya laboratuvari vb tiplere ayrilirlar. Ilgili notlarla
    birlikte bu tipler RoomType modelinde tanimlanir.

    """

    type = field.String(_(u"Oda Tipi"), index=True)
    notes = field.Text(_(u"Notlar"), index=True)
    exam_available = field.Boolean(_(u"Sınav Amaçlı Kullanılabilir"), index=True)

    class Meta:
        verbose_name = _(u"Oda Tipi")
        verbose_name_plural = _(u"Oda Tipleri")
        search_fields = ['type', 'notes']
        list_fields = ['type', ]

    def __unicode__(self):
        return '%s' % self.type


class Room(Model):
    """Oda modeli

    Üniversitenin sahip olduğu odalara (sınıf, lab, amfi) ait data modelidir. Her odanın
    bir kodu bulunur.

    Odalar, binalara ve binalar aracılığıyla kampüslere bağlanır.

    """

    code = field.String(_(u"Kod"), index=True)
    name = field.String(_(u"İsim"), index=True)
    room_type = RoomType(_(u"Oda Tipi"), index=True)
    unit = Unit(_(u"Bölüm"))

    #: Bina içerisindeki kat bilgisi
    floor = field.String(_(u"Kat"), index=True)
    capacity = field.Integer(_(u"Kapasite"), index=True)
    building = Building()
    exam_capacity = field.Integer(_(u"Sınav Kapasitesi"))

    is_active = field.Boolean(_(u"Aktif"), index=True)
    unitime_key = field.String()  # Ders/Sınav programları hazırlanırken id'leri eşleştirmek için

    class Meta:
        verbose_name = _(u"Oda")
        verbose_name_plural = _(u"Odalar")
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.capacity)
