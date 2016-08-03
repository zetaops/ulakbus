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
from ulakbus.models import Unit

__author__ = 'Ali Riza Keles'


class Campus(Model):
    """Kampüs Modeli

    Üniversite kampüslerine ait data modeli. Kampus adı ve koordinat bilgilerini içerir.

    Kampüs koordinatları lokasyon bazlı hesaplamalar için kullanılacaktır. Özellikle
    Unitime ile ders programı hazırlarken farklı lokasyonlar arası zaman hesaplamalarında
    kullanılmaktadır.

    """

    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    coordinate_x = field.String("X Koordinatı", index=True)
    coordinate_y = field.String("Y Koordinatı", index=True)

    class Meta:
        verbose_name = "Yerleşke"
        verbose_name_plural = "Yerleşkeler"
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

    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    coordinate_x = field.String("X Koordinatı", index=True)
    coordinate_y = field.String("Y Koordinatı", index=True)
    campus = Campus()

    class Meta:
        verbose_name = "Bina"
        verbose_name_plural = "Binalar"
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

    type = field.String("Oda Tipi", index=True)
    notes = field.Text("Notlar", index=True)
    exam_available = field.Boolean("Sınav Amaçlı Kullanılabilir", index=True)

    class Meta:
        verbose_name = "Oda Tipi"
        verbose_name_plural = "Oda Tipleri"
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

    code = field.String("Kod", index=True)
    name = field.String("İsim", index=True)
    room_type = RoomType("Oda Tipi", index=True)

    #: Bina içerisindeki kat bilgisi
    floor = field.String("Kat", index=True)
    capacity = field.Integer("Kapasite", index=True)
    building = Building()

    is_active = field.Boolean("Aktif", index=True)
    unitime_key = field.String()  # Ders/Sınav programları hazırlanırken id'leri eşleştirmek için

    class Meta:
        verbose_name = "Oda"
        verbose_name_plural = "Odalar"
        search_fields = ['code', 'name']
        list_fields = ['code', 'name']

    class RoomDepartments(ListNode):
        """Oda Departman ListNode

        Bu odayı kullanabilecek birimlerin listesi saklanır.

        """

        unit = Unit()

    def __unicode__(self):
        return '%s %s %s' % (self.code, self.name, self.capacity)
