# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import time
from pyoko import Model, field, ListNode
from ulakbus.lib.date_time_helper import gun_dilimi_listele, HAFTA, gun_listele
from ulakbus.models import RoomType, Sube, Donem, Ders, Ogrenci
from zengine.forms import fields
from zengine.lib.translation import gettext_lazy as _, gettext, format_time, format_datetime
from .buildings_rooms import Room
from .auth import Unit
from .ogrenci import Okutman
import random


def uygunluk_durumu_listele():
    return [
        (1, gettext(u"Uygun")),
        (2, gettext(u"Mümkünse Uygun Değil")),
        (3, gettext(u"Kesinlikle Uygun Değil"))
    ]


def derslik_durumu_listele():
    return [
        (1, gettext(u'Herkese Açık')),
        (2, gettext(u'Bölüme Ait')),
        (3, gettext(u'Herkese Kapalı')),
    ]


class ZamanDilimleri(Model):
    class Meta:
        verbose_name = _(u"Zaman Dilimi")
        verbose_name_plural = _(u"Zaman Dilimleri")
        unique_together = [('birim', 'gun_dilimi')]
        search_fields = ['birim', 'gun_dilimi']

    birim = Unit(_(u'Bölüm'))
    gun_dilimi = field.Integer(_(u'Gün Dilimi'), choices=gun_dilimi_listele, index=True)

    baslama_saat = field.String(_(u"Başlama Saati"), index=True)
    baslama_dakika = field.String(_(u"Başlama Dakikası"), index=True)

    bitis_saat = field.String(_(u"Bitiş Saati"), index=True)
    bitis_dakika = field.String(_(u"Bitiş Dakikası"), index=True)

    # Ara suresi de dahil. Ornek olarak 30 girildiyse ders 9, 9.30, 10 gibi surelerde baslayabilir.
    ders_araligi = field.Integer(_(u'Ders Süresi'), default=60, index=True)
    ara_suresi = field.Integer(_(u'Tenefüs Süresi'), default=10, index=True)

    zaman_dilimi_suresi = field.Integer(_(u"Zaman Dilimi Süresi"), index=True)

    def pre_save(self):
        self.zaman_dilimi_suresi = int(self.bitis_saat) - int(self.baslama_saat)

    def __unicode__(self):
        return '%s - %s|%s' % (
            dict(gun_dilimi_listele())[int(self.gun_dilimi)],
            format_time(time(int(self.baslama_saat), int(self.baslama_dakika))),
            format_time(time(int(self.baslama_dakika), int(self.bitis_dakika))),
        )


class OgElemaniZamanPlani(Model):
    """
        Okutman, birim ve okutmanin ilgili birimde verecegi  haftalik ders saati bilgisi tutulur.
    """

    class Meta:
        verbose_name = _(u'Öğretim Elemanı Zaman Kaydı')
        verbose_name_plural = _(u'Öğretim Elemanı Zaman Kayıtları')
        unique_together = [('okutman', 'birim')]
        search_fields = ['okutman', 'birim']

    okutman = Okutman(_(u"Öğretim Elemanı"))
    birim = Unit(_(u"Birim"))
    toplam_ders_saati = field.Integer(_(u"Öğretim Elemanı Toplam Ders Saati"), index=True)

    def __unicode__(self):
        return '%s - %s' % (self.birim, self.okutman)


class ZamanCetveli(Model):
    """
        Ilgili birime ait belirlenen zaman dilimleri ders program koordinatoru tarafindan
        ogretim elemanlarin saat araliklarina gore durumlarini belirleyecegi model
    """

    class Meta:
        verbose_name = _(u'Zaman Cetveli')
        verbose_name_plural = _(u'Zaman Cetvelleri')

        unique_together = [('zaman_dilimi', 'ogretim_elemani_zaman_plani', 'gun')]
        search_fields = ['zaman_dilimi', 'ogretim_elemani_zaman_plani', 'birim', 'gun', 'durum']

    birim = Unit(_(u"Birim"))
    gun = field.Integer(_(u"Gün"), choices=gun_listele, index=True)
    zaman_dilimi = ZamanDilimleri(_(u"Zaman Dilimi"))
    durum = field.Integer(
        _(u"Uygunluk Durumu"),
        choices=uygunluk_durumu_listele,
        default=1, index=True
    )
    ogretim_elemani_zaman_plani = OgElemaniZamanPlani(_(u"Öğretim Elemanı"))

    def __unicode__(self):
        return '%s - %s - %s' % (self.ogretim_elemani_zaman_plani, self.zaman_dilimi,
                                 dict(uygunluk_durumu_listele())[int(self.durum)])


class DerslikZamanPlani(Model):
    class Meta:
        verbose_name = _(u'Derslik Zaman Planı')
        verbose_name_plural = _(u'Derslik Zaman Planları')

        unique_together = [
            ('derslik', 'gun', 'baslangic_saat', 'baslangic_dakika', 'bitis_saat', 'bitis_dakika')]
        search_fields = ['unit', 'derslik', 'gun', 'derslik_durum']

    birim = Unit()
    derslik = Room()
    gun = field.Integer(_(u"Gün"), choices=gun_listele, index=True)
    baslangic_saat = field.String(_(u'Başlangıç Saati'), default='08', index=True)
    baslangic_dakika = field.String(_(u'Başlangıç Dakikası'), default='30', index=True)
    bitis_saat = field.String(_(u"Bitiş Saati"), default='12', index=True)
    bitis_dakika = field.String(_(u"Bitiş Dakikası"), default='00', index=True)
    durum = field.Integer(_(u"Durum"), choices=derslik_durumu_listele, index=True)

    def __unicode__(self):
        return '%s %s %s|%s %s' % (
            self.derslik,
            dict(HAFTA)[self.gun],
            format_time(time(int(self.baslangic_saat), int(self.baslangic_dakika))),
            format_time(time(int(self.bitis_saat), int(self.bitis_dakika))),
            dict(derslik_durumu_listele())[int(self.derslik_durum)]
        )

    @staticmethod
    def kullanabilen_bolumler(derslik, **kwargs):
        units = set(DerslikZamanPlani.objects.filter(derslik=derslik, **kwargs).values_list('unit_id'))
        return units

    @staticmethod
    def kullanabildigi_derslikler(unit, make_object=True, **kwargs):
        rooms = set(DerslikZamanPlani.objects.filter(unit=unit, **kwargs).values_list('derslik_id'))
        if make_object:
            return map(Room.objects.get, rooms)
        else:
            return rooms


class DersEtkinligi(Model):
    class Meta:
        verbose_name = _(u"Ders Etkinliği")
        verbose_name_plural = _(u"Ders Etkinlikleri")
        search_fields = ['unit_yoksis_no', 'room', 'okutman']

    solved = fields.Boolean(_(u'Ders Planı Çözüm Durumu'), index=True)
    unitime_key = fields.String(index=True)  # class id
    unit_yoksis_no = fields.Integer(_(u'Bölüm Yöksis Numarası'), index=True)
    room_type = RoomType(_(u'İşleneceği Oda Türü'), index=True)
    okutman = Okutman(_(u"Öğretim Elemanı"), index=True)
    sube = Sube(_(u'Şube'), index=True)
    donem = Donem(_(u'Dönem'), index=True)
    bolum = Unit(_(u'Bölüm'), index=True)
    published = fields.Boolean(_(u'Ders Planı Yayınlanma Durumu'), index=True)
    # Arama amaçlı
    ders = Ders(_(u'Ders'), index=True)
    ek_ders = fields.Boolean(index=True)
    sure = fields.Integer("Ders Etkinliği Süresi", index=True)

    # teori = field.Integer("Ders Teori Saati", index=True)
    # uygulama = field.Integer("Ders Uygulama Saati", index=True)
    # dersin süresinin ne kadarı teori ne kadarı uygulama gibi 2+2, 4+0 gibi

    # to be calculated
    room = Room(_(u'Derslik'))
    gun = fields.String(_(u"Gün"), choices=gun_listele)
    baslangic_saat = fields.String(_(u"Başlangıç Saati"))
    baslangic_dakika = fields.String(_(u"Başlangıç Dakikası"))
    bitis_saat = fields.String(_(u"Bitiş Saati"))
    bitis_dakika = fields.String(_(u"Bitiş Dakikası"))

    def post_creation(self):
        """Yeni bir DersEtkinligi oluşturulduğunda arama amaçlı olan
        alanları otomatik olarak doldurur."""
        self.ders = self.sube.ders
        self.save()

    def __unicode__(self):
        return '%s - %s - %s:%s|%s:%s - %s' % (
            self.room.name, self.gun, self.baslangic_saat, self.baslangic_dakika,
            self.bitis_saat, self.bitis_dakika, self.okutman)


class SinavEtkinligi(Model):
    class Meta:
        verbose_name = _(u'Sınav Etkinliği')
        verbose_name_plural = _(u'Sınav Etkinlikleri')
        search_field = ['bolum', 'ders', 'sube', 'donem']

    sube = Sube(_(u'Şube'), index=True)
    ders = Ders(_(u'Ders'), index=True)
    donem = Donem(_(u'Dönem'), index=True)
    bolum = Unit(_(u'Bölüm'), index=True)
    unitime_key = fields.String(index=True)
    # default False, unitime solver tarafindan True yapilir.
    solved = fields.Boolean(_(u'Sınav Planı Çözüm Durumu'), index=True, default=False)

    # unitime cozumunun ardindan, is akisiyla sinav takvimi yayinlanip True yapilir.
    published = fields.Boolean(_(u'Sınav Planı Yayınlanma Durumu'), index=True, default=False)

    # sistem servisiyle sinavlarin ardindan True yapilir.
    archived = fields.Boolean(_(u'Arşivlenmiş'), default=False, index=True)

    tarih = fields.DateTime(_(u'Sınav Tarihi'), index=True)

    class SinavYerleri(ListNode):
        room = Room(_(u'Sınav Yeri'), index=True)

    class Ogrenciler(ListNode):
        ogrenci = Ogrenci(_(u'Öğrenci'))
        room = Room(_(u'Sınav Yeri'), index=True)

    @classmethod
    def aktif_bolum_sinav_etkinlik_listesi(cls, donem, bolum):
        """
        Verilen bölümün aktif yayınlanmış sınav etkinliklerinin
        listesini döndürür.

        """
        return [e for e in
                cls.objects.filter(published=True, archived=False, donem=donem, bolum=bolum)]

    def sinav_ogrenci_listesi(self):
        """
        Verilen sınav etkinliğine katılacak olan öğrencilerin
        listesini döndürür.

        """
        return [e.ogrenci for e in self.Ogrenciler]

    def doluluk_orani_hesapla(self):
        """
        Bir sınav etkinliğine kayıtlı olan öğrencilerin sayısı ile
        etkinliğin yapılacak sınav yerlerinin toplam kontenjan sayısının
        birbirine bölünmesi ile elde edilen oranı döndürür. Bu oran öğrencileri
        odalara dengeli şekilde dağıtmak için kullanılacaktır.

        """
        toplam_kontenjan = sum([e.room.capacity for e in self.SinavYerleri])
        doluluk_orani = len(self.Ogrenciler) / float(toplam_kontenjan)

        return doluluk_orani

    def ogrencileri_odalara_dagit(self, doluluk_orani):
        """
        Öğrencileri sınavın yapılacağı odalara doluluk oranını
        göz önüne alarak dengeli bir şekilde dağıtır.

        """
        from math import ceil
        random.shuffle(self.Ogrenciler)
        j = 0
        for sinav_yeri in self.SinavYerleri:
            temp = j + int(ceil(sinav_yeri.room.capacity * doluluk_orani))
            i = j
            j = temp
            for ogrenci in self.Ogrenciler[i:j]:
                ogrenci.room = sinav_yeri.room

        self.save()

    @classmethod
    def ogrencileri_odalara_rastgele_ata(cls, bolum):
        """
        Bir bölümün yayınlanmış sınav programındaki her bir sınav etkinliğine
        katılacak olan öğrencileri, sınavın yapılabilineceği odalara rastgele
        atar, bu atamayı yaparken kontenjan sınırını aşmamasına dikkat edilir.

        """
        donem = Donem.guncel_donem()
        aktif_sinav_etkinlikleri = cls.aktif_bolum_sinav_etkinlik_listesi(donem, bolum)
        for etkinlik in aktif_sinav_etkinlikleri:
            doluluk_orani = etkinlik.doluluk_orani_hesapla()
            etkinlik.ogrencileri_odalara_dagit(doluluk_orani)

    def ogrenci_sinav_oda_getir(self, ogrenci):
        """
        Verilen öğrencinin sınava gireceği oda bilgisini döndürür.

        """
        for ogrenci_oda in self.Ogrenciler:
            if ogrenci_oda.ogrenci == ogrenci:
                break

        return ogrenci_oda.room

    @classmethod
    def sube_sinav_listesi(cls, sube, archived=False, donem=None):
        """
        Şubeye, döneme ve arşive göre sınav etkinliği listesi döndürür.

        """
        donem = donem or Donem.guncel_donem()
        return [e for e in cls.objects.filter(
            published=True,
            sube=sube,
            archived=archived,
            donem=donem
        ).order_by('-tarih')]

    def __unicode__(self):
        return '{} {} {}'.format(self.ders.ad, self.sube.ad, self.sinav_zamani())

    def sinav_zamani(self):
        return format_datetime(self.tarih) if self.tarih else _(u'Henüz zamanlanmadi')


class SinavZamanDilimi(Model):
    class Meta:
        verbose_name = _(u'Sınav Zaman Dilimi')
        verbose_name_plural = _(u'Sınav Zaman Dilimleri')
        unique_together = [('birim', 'gun_dilimi')]
        search_fields = ['birim', 'gun_dilimi']

    birim = Unit(_(u'Bölüm'))
    gun_dilimi = field.Integer(_(u'Gün Dilimi'), choices=gun_dilimi_listele)
    baslama_saat = field.String(_(u"Başlama Saati"))
    baslama_dakika = field.String(_(u"Başlama Dakikası"))

    bitis_saat = field.String(_(u"Bitiş Saati"))
    bitis_dakika = field.String(_(u"Bitiş Dakikası"))

    def __unicode__(self):
        return '{}/{}:{}-{}:{}'.format(dict(gun_dilimi_listele())[self.gun_dilimi], self.baslama_saat, self.baslama_dakika,
                                       self.bitis_saat, self.bitis_dakika)


class DerslikSinavPlani(Model):
    class META:
        verbose_name = _(u'Derslik Sınav Planı')
        verbose_name_plural = _(u'Derslik Sınav Planları')
        unique_together = [('derslik', 'zaman_dilimi', 'birim', 'gun')]
        search_fields = ['derslik', 'birim', 'zaman_dilimi', 'gun', 'durum']

    derslik = Room(_(u'Derslik'))
    birim = Unit(_(u'Bölüm'))
    donem = Donem(_(u'Güncel Dönem'))
    zaman_dilimi = SinavZamanDilimi(_(u'Sınav Zaman Dilimi'))
    durum = field.Integer(_(u"Uygunluk Durumu"), choices=uygunluk_durumu_listele(), default=1, index=True)
    gun = field.Integer(_(u"Gün"), choices=HAFTA)

    def __unicode__(self):
        return '{}/{}/{}'.format(dict(HAFTA)[self.gun], self.zaman_dilimi,
                                 dict(uygunluk_durumu_listele())[self.durum])
