# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from zengine.lib.translation import gettext as _, gettext_lazy
from ulakbus.models.ogrenci import Okutman, Donem, Takvim, Unit, Personel
from ulakbus.models.personel import Izin
from datetime import datetime
import calendar
from collections import OrderedDict
from ulakbus.lib.date_time_helper import AYLAR, ay_listele
from ulakbus.views.reports import ders_ucreti_hesaplama as DU

guncel_yil = datetime.now().year
guncel_ay = datetime.now().month

# Guncel donem ve 5 onceki yili tuple halinde YIL listesinde tutar.
YIL = []
for i in range(5):
    YIL.append((i, guncel_yil - i))


class TarihForm(JsonForm):
    """
    Puantaj tablosu hazırlanırken ay ve yıl seçiminde
    kullanılan form.
    """

    class Meta:
        title = gettext_lazy(u'Puantaj Tablosu Hazırlamak İstediğiniz Yıl ve Ayı Seçiniz')

    yil_sec = fields.String(_(u'Yıl Seçiniz'), choices=YIL, default=0)
    ay_sec = fields.String(_(u'Ay Seçiniz'), choices=ay_listele, default=guncel_ay)


class OkutmanListelemeForm(JsonForm):
    """
    Puantaj tablosu hazırlanacak olan okutmanların listesini
    gösteren form.
    """

    class Meta:
        inline_edit = ['secim']

    class OkutmanListesi(ListNode):
        secim = fields.Boolean(_(u"Seçim"), type="checkbox")
        okutman = fields.String(_(u'Okutman'), index=True)
        key = fields.String(hidden=True)


class DersUcretiHesaplama(CrudView):
    """
    Tüm okutmanların aylık olarak girdikleri derslerin
    ve ek derslerin saatlerini hesaplamaya yarayan iş akışı.
    Izin gunleri ve resmi tatil gunlerini de dikkate alir.
    """

    def tarih_sec(self):
        """
        Puantaj tablosunun hesaplanacağı ay ve yılı
        seçmeye yarar.
        """

        _form = TarihForm(current=self.current)
        _form.sec = fields.Button(_(u"İlerle"))
        self.form_out(_form)

    def donem_kontrol(self):
        """
        Seçilen ay ve yıla ait dönem olup olmadığını kontrol eder.
        """

        self.current.task_data["yil"] = YIL[self.input['form']['yil_sec']][1]
        self.current.task_data["ay"] = self.input['form']['ay_sec']
        # guncel olan ayın ismi getirilir.
        self.current.task_data["ay_isim"] = AYLAR[self.input['form']['ay_sec'] - 1][1]

        takvim = calendar.monthrange(self.current.task_data["yil"], self.current.task_data["ay"])
        donem_list = Donem.takvim_ayina_rastlayan_donemler(self.current.task_data["yil"], self.current.task_data["ay"], takvim)

        if len(donem_list) > 0:
            self.current.task_data['donem_sayi'] = True
        else:
            self.current.task_data['donem_sayi'] = False

    def donem_secim_uyari(self):
        """
        Eğer seçilen ay ve yıla ait dönem bulunamamışsa uyarı verir.
        2016 Güz dönemindeyken 2016 Temmuz ayı (Yaz Dönemi) için bir sorgu
        istenirse daha o dönem açılmadığından hata verecektir.
        """

        _form = JsonForm(current=self.current, title=_(u"Dönem Bulunamadı"))
        _form.help_text = _(u"""Seçtiğiniz yıl ve aya ait dönem bulunamadı. Tarih
                          seçimine geri dönmek için Geri Dön butonuna, işlemi
                          iptal etmek için İptal butonuna basabilirsiniz.""")
        _form.geri_don = fields.Button(_(u"Geri Dön"), flow='tarih_sec')
        _form.iptal = fields.Button(_(u"İptal"))
        self.form_out(_form)

    def islem_iptali_bilgilendir(self):

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Durum Mesajı'),
            "msg": _(u'Puantaj cetveli görüntüleme işleminiz iptal edilmiştir.')
        }

    def ders_saati_turu_secme(self):
        """
        Ders Ücreti ya da Ek Ders Ücreti hesaplarından birini seçmeye yarar.
        """

        _form = JsonForm(current=self.current, title=_(u"Öğretim Görevlileri "
                                                       u"Puantaj Tablosu Hesaplama "
                                                       u"Türü Seçiniz"))

        _form.ders = fields.Button(_(u"Ders Ücreti Hesapla"), cmd='ders_ucreti_hesapla')
        _form.ek_ders = fields.Button(_(u"Ek Ders Ücreti Hesapla"), cmd='ek_ders_ucreti_hesapla')
        self.form_out(_form)

    def ders_ucreti_hesapla(self):

        self.current.task_data["control"] = True

    def ek_ders_ucreti_hesapla(self):
        self.current.task_data["control"] = False

    def ucret_hesapla(self):
        """
        Seçilen ay ve yıla göre, seçilen her bir öğretim elemanının
        resmi tatil ve izinleri dikkate alarak aylık ders saati planlamasını
        yapar
        """
        okutman_personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=okutman_personel)
        okutman_adi = okutman.ad + ' ' + okutman.soyad

        yil = self.current.task_data["yil"]  # girilen yil
        ay = self.current.task_data["ay"]  # girilen ayin orderi
        ay_isim = self.current.task_data["ay_isim"]  # ayin adi

        takvim = calendar.monthrange(yil, ay)
        # verilen yıl ve aya göre tuple şeklinde ayın ilk gününü
        # ve ayın kaç gün sürdüğü bilgisini döndürür.
        # Ayın ilk günü = 0-6 Pazt-Pazar
        # 2016 yılı Temmuz ayı için = (4,31)

        birim_no = self.current.role.unit.yoksis_no  # rolden gelecek
        birim_unit = Unit.objects.get(yoksis_no=birim_no)

        # Secilen ay hangi donemleri kapsiyor, kac donemi kapsıyorsa
        # o donemleri dondürür.
        donem_list = Donem.takvim_ayina_rastlayan_donemler(yil, ay, takvim)

        # Resmi tatilerin gununu (23, 12, 8) gibi ve doneme gore akademik takvim donduruyor
        resmi_tatil_list, akademik_takvim_list = Takvim.resmi_tatil_gunleri_getir(donem_list, birim_unit, yil, ay)

        # Kapsadığı dönemlere göre ders baslangıc ve bitis tarihlerini
        # baz alarak kapsadığı her bir dönemin seçilen ayda hangi gün
        # aralıklarını kapsadığı bilgisini tuple olarak dondurur. Bir
        # dönemi kapsıyorsa bir tuple, iki dönemi kapsıyorsa iki tuple
        # döner. (4,12) (19,31) gibi
        tarih_araligi = DU.donem_aralik_dondur(donem_list, yil, ay, takvim, akademik_takvim_list)

        object_list = ['Öğretim Elemanı']
        tarih_list = list(range(1, takvim[1] + 1))
        for tarih in tarih_list:
            object_list.append(' ' + str(tarih))

        # object_list = ['Ogretim Elemani', 'bir', 'iki', 'uc']
        _form = JsonForm(current=self.current)

        kontrol = self.current.task_data["control"]
        if kontrol:
            _form.title = _(u"%(ad)s - %(birim)s %(yil)s-%(ay)s AYI DERS PUANTAJ TABLOSU") % {
                'ad': okutman_adi.upper(),
                'birim': birim_unit.name,
                'yil': yil,
                'ay': ay_isim.upper()}
            ders_saati_turu = _(u'Ders Saati')

        else:
            _form.title = _(u"%s - %s %s-%s AYI EK DERS PUANTAJ TABLOSU") % (
            okutman_adi.upper(), birim_unit.name, yil, ay_isim.upper())
            ders_saati_turu = _(u'Ek Ders Saati')

        object_list.append(ders_saati_turu)
        self.output['objects'] = [object_list]

        data_list = OrderedDict({})

        # Seçilen okutmanın İzin ve Ücretsiz İzinlerini dikkate alarak, verilen ayda
        # hangi günler izinli olduğunu liste halinde döndürmeye yarayan method
        # [17,18,19] gibi
        personel_izin_list = Izin.personel_izin_gunlerini_getir(okutman, yil, ay)

        # Verilen döneme ve okutmana göre, haftada hangi gün kaç saat dersi
        # (seçilen seçeneğe göre ders veya ek ders) olduğunu gösteren
        # dictionarylerden oluşan liste, seçilen yıl ve ay bir dönemi kapsıyorsa
        # bir dict, iki dönemi kapsıyorsa iki dict döner.
        ders_etkinlik_list = DU.okutman_etkinlikleri_hesaplama(donem_list, okutman, kontrol)

        # Bulunan tarih araliklarina, okutmanın aylık ders etkinliklerine göre
        # ayın hangi gününde dersi varsa kaç saat dersi olduğu bilgisi,
        # izinliyse İ, resmi tatilse R bilgisini bir dictionary e doldurur.
        okutman_aylik_plan, ders_saati = DU.ders_saati_doldur(donem_list, ders_etkinlik_list,
                                                              resmi_tatil_list, personel_izin_list,
                                                              tarih_araligi, yil, ay)

        data_list['Öğretim Elemanı'] = okutman_adi

        for gun in range(1, takvim[1] + 1):
            if gun in okutman_aylik_plan:
                data_list[' ' + str(gun)] = str(okutman_aylik_plan[gun])
            else:
                data_list[' ' + str(gun)] = ' '

        data_list[ders_saati_turu] = str(ders_saati)

        item = {
            "type": "table-multiRow",
            "fields": data_list,
            "actions": False,
            'key': okutman.key
        }

        self.output['objects'].append(item)

        _form.pdf_sec = fields.Button(_(u"Pdf Çıkar"))
        _form.help_text = _(u"""
                         R: Resmi Tatil
                         İ: İzinli""")
        self.form_out(_form)
