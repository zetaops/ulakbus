# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.models.ogrenci import Okutman, Donem, Takvim, Unit
from ulakbus.models.personel import Izin
from ulakbus.models.ders_sinav_programi import DersEtkinligi
from datetime import datetime, date
import calendar
from collections import OrderedDict
from ulakbus.lib.date_time_helper import AYLAR

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

    yil_sec = fields.String('Yıl Seçiniz', choices=YIL, default=0)
    ay_sec = fields.String('Ay Seçiniz', choices=AYLAR, default=guncel_ay)


class OkutmanListelemeForm(JsonForm):
    """
    Puantaj tablosu hazırlanacak olan okutmanların listesini
    gösteren form.
    """

    class Meta:
        inline_edit = ['secim']

    class OkutmanListesi(ListNode):
        secim = fields.Boolean("Seçim", type="checkbox")
        okutman = fields.String('Okutman', index=True)
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
        _form.title = 'Puantaj Tablosu Hazırlamak İstediğiniz Yıl ve Ayı Seçiniz'
        _form.sec = fields.Button("İlerle")
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

        _form = JsonForm(current=self.current, title="Dönem Bulunamadı")
        _form.help_text = """Seçtiğiniz yıl ve aya ait dönem bulunamadı. Tarih
                          seçimine geri dönmek için Geri Dön butonuna, işlemi
                          iptal etmek için İptal butonuna basabilirsiniz."""
        _form.geri_don = fields.Button("Geri Dön", flow='tarih_sec')
        _form.iptal = fields.Button("İptal")
        self.form_out(_form)

    def islem_iptali_bilgilendir(self):

        """
        İşlem iptal edildiğinde kullanıcı iptal hakkında bilgilendirilir.
        """

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Durum Mesajı',
            "msg": 'Puantaj cetveli görüntüleme işleminiz iptal edilmiştir.'
        }

    def okutman_sec(self):
        """
        Puantaj tablosunun hesaplanacağı okutmanların
        seçilmesine yarar. Bu okutmanlar işlem yapılan birime göre
        sorgulatılır. Bilgisayar Mühendisliği için yapılan sorguda
        sadece Bilgisayar Mühendisliği'nde bulunan okutmanlar ekrana
        gelecektir.
        """

        birim_no = self.current.role.unit.yoksis_no
        _form = OkutmanListelemeForm(current=self.current, title="Okutman Seçiniz")
        okutmanlar = Okutman.objects.filter(birim_no=birim_no)

        for okutman in okutmanlar:
            okutman_adi = okutman.ad + ' ' + okutman.soyad

            _form.OkutmanListesi(secim=True, okutman=okutman_adi, key=okutman.key)

        _form.sec = fields.Button("İlerle")
        self.form_out(_form)

    def okutman_secim_kontrol(self):

        """
        İşlem yapılacak öğretim görevlisi seçilip seçilmediğini kontrol eder.
        """

        self.current.task_data["control"] = None
        secilen_okutmanlar = []
        for okutman_secim in self.current.input['form']['OkutmanListesi']:
            if okutman_secim['secim'] == True:
                secilen_okutmanlar.append(okutman_secim)

        self.current.task_data["secilen_okutmanlar"] = secilen_okutmanlar

        if len(secilen_okutmanlar)>0:
            self.current.task_data["okutman_kontrol"] = True
        else:
            self.current.task_data["okutman_kontrol"] = False

    def okutman_secim_uyari(self):

        """
        Hiç öğretim görevlisi seçilmediği durumda, uyarı verir.
        """

        _form = JsonForm(current=self.current, title="Öğretim Görevlisi Seçmelisiniz")
        _form.help_text = """İşlem yapabilmek için en az bir öğretim görevlisi seçmelisiniz.
                             Öğretim görevlisi s    eçimine geri dönmek için Geri Dön butonuna,
                             işlemi iptal etmek için İptal butonuna basabilirsiniz."""
        _form.geri_don = fields.Button("Geri Dön", flow='okutman_sec')
        _form.iptal = fields.Button("İptal")
        self.form_out(_form)

    def ders_saati_turu_secme(self):
        """
        Ders Ücreti ya da Ek Ders Ücreti hesaplarından birini seçmeye yarar.
        """

        _form = JsonForm(current=self.current, title=
        "Öğretim Görevlileri Puantaj Tablosu Hesaplama Türü Seçiniz")

        _form.ders = fields.Button("Ders Ücreti Hesapla", cmd='ders_ucreti_hesapla')
        _form.ek_ders = fields.Button("Ek Ders Ücreti Hesapla", cmd='ek_ders_ucreti_hesapla')
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

        yil = self.current.task_data["yil"]  # girilen yil
        ay = self.current.task_data["ay"]  # girilen ayin orderi
        ay_isim = self.current.task_data["ay_isim"]  # ayin adi

        takvim = calendar.monthrange(yil, ay)
        # verilen yıl ve aya göre tuple şeklinde ayın ilk gününü
        # ve ayın kaç gün sürdüğü bilgisini döndürür.
        # Ayın ilk günü = 0-6 Pazt-Pazar
        # 2016 yılı Temmuz ayı için = (4,31)

        birim_unit = Unit.objects.get(yoksis_no=self.current.role.unit.yoksis_no)

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
        tarih_araligi = donem_aralik_dondur(donem_list, yil, ay, takvim, akademik_takvim_list)

        object_list = ['Öğretim Elemanı']
        tarih_list = list(range(1, takvim[1] + 1))

        # integer kabul etmedigi icin bosluk + integer koyuldu.
        # sonradan degistirilecek.
        for tarih in tarih_list:
            object_list.append(' ' + str(tarih))

        _form = JsonForm(current=self.current)

        kontrol = self.current.task_data["control"]
        if kontrol:
            _form.title = "%s %s-%s AYI DERS PUANTAJ TABLOSU" % (birim_unit.name, yil, ay_isim.upper())
            ders_saati_turu = 'Ders Saati'

        else:
            _form.title = "%s %s-%s AYI EK DERS PUANTAJ TABLOSU" % (birim_unit.name, yil, ay_isim.upper())
            ders_saati_turu = 'Ek Ders Saati'

        object_list.append(ders_saati_turu)
        self.output['objects'] = [object_list]

        for secilen_okutman in self.current.task_data["secilen_okutmanlar"]:
            okutman = Okutman.objects.get(secilen_okutman['key'])

            data_list = OrderedDict({})

            # Seçilen okutmanın İzin ve Ücretsiz İzinlerini dikkate alarak, verilen ayda
            # hangi günler izinli olduğunu liste halinde döndürmeye yarayan method
            # [17,18,19] gibi
            personel_izin_list = Izin.personel_izin_gunlerini_getir(okutman, yil, ay)

            okutman_adi = okutman.ad + ' ' + okutman.soyad

            # Verilen döneme ve okutmana göre, haftada hangi gün kaç saat dersi
            # (seçilen seçeneğe göre ders veya ek ders) olduğunu gösteren
            # dictionarylerden oluşan liste, seçilen yıl ve ay bir dönemi kapsıyorsa
            # bir dict, iki dönemi kapsıyorsa iki dict döner.
            ders_etkinlik_list = okutman_etkinlikleri_hesaplama(donem_list, okutman, kontrol)

            # Bulunan tarih araliklarina, okutmanın aylık ders etkinliklerine göre
            # ayın hangi gününde dersi varsa kaç saat dersi olduğu bilgisi,
            # izinliyse İ, resmi tatilse R bilgisini bir dictionary e doldurur.
            okutman_aylik_plan, ders_saati = ders_saati_doldur(donem_list, ders_etkinlik_list,
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

        _form.pdf_sec = fields.Button("Pdf Çıkar")
        _form.help_text = """
                         R: Resmi Tatil
                         İ: İzinli"""
        self.form_out(_form)


def ders_saati_doldur(donem_list, ders_etkinlik_list, resmi_tatil_list, personel_izin_list, tarih_araligi, yil, ay):
    ders_saati = 0
    okutman_aylik_plan = {}

    # Tarih aralığı bir tuple olduğu için
    # her bir dönem için o dönemin tarih aralığı
    # dikkate alınır.
    for j, donem in enumerate(donem_list):
        okutman_ders_dict = ders_etkinlik_list[j]

        # Dönemi kapsıyor fakat ders etkinliği yoksa, döngünün dönmemesi
        # için tuple'dan bir eksiltilir. (1,1) ise (1,0) yapılır. Çünkü
        # döngü range'inde tuple'ın ikinci elemanı bir arttırılıyor.
        if tarih_araligi[j][0]==tarih_araligi[j][1]:
            tarih_araligi[j]=(tarih_araligi[j][0], tarih_araligi[j][1] -1)

        for i in range(tarih_araligi[j][0], tarih_araligi[j][1] +1):

            gun = calendar.weekday(yil, ay, i) + 1
            # calendar haftanın günlerini 0-6, biz 1-7
            # olarak aldığımız için 1 ile toplanıyor.

            # Eğer gün personel izin listesinde varsa
            if i in personel_izin_list:
                okutman_aylik_plan[i] = 'İ'

            # Eğer gün personel izin listesinde varsa
            elif i in resmi_tatil_list[j]:
                okutman_aylik_plan[i] = 'R'

            # Eğer o gün izinli ya da resmi tatil değilse
            # ve dersi varsa dictin gün keyine kaç saat olduğu
            # value'su eklenir ve ders saati arttırılır.
            elif gun in okutman_ders_dict:
                okutman_aylik_plan[i] = okutman_ders_dict[gun]
                ders_saati += okutman_ders_dict[gun]

    return okutman_aylik_plan, ders_saati


def okutman_etkinlikleri_hesaplama(donem_list, okutman, kontrol):
    ders_etkinlik_list = []
    # kontrol ders ya da ek ders hesaplamasını gösterir.
    # Eğer kontrol True ise ders, False ise ek ders hesaplanır.

    # Verilen dönemde okutmanın hangi günler kaç saat dersi olduğu
    # bilgisini dict halinde döndürür. Günler 1-7 Pazt-Pazar
    # şeklinde belirlenmiştir. Örnek: {1:4, 3:3,4:2} gibi. Bu
    # dict bize okutmanın Pazartesi 4 saat, Çarşamba günü 3 saatlik
    # dersi olduğunu gösterir.
    for donem in donem_list:

        okutman_ders_dict = {}

        for etkinlik in DersEtkinligi.objects.filter(donem=donem, okutman=okutman, ek_ders=not kontrol):

            if not etkinlik.gun in okutman_ders_dict:
                okutman_ders_dict[etkinlik.gun] = etkinlik.sure
            else:
                okutman_ders_dict[etkinlik.gun] += etkinlik.sure

        ders_etkinlik_list.append(okutman_ders_dict)

    return ders_etkinlik_list


def donem_aralik_dondur(donem_list, yil, ay, takvim, akademik_takvim_list):
    tarih_araligi = []

    # Hangi dönemin ders başlangıç ve bitiş tarihini
    # dikkate almak için Akademik Takvim'de bulunan etkinlik
    # döneme göre seçilir.
    for j, donem in enumerate(donem_list):

        # İçinde bulunulan dönemin ders başlangıç ve bitiş tarihlerini
        # bulmak için kullanılır.

        if 'Güz' in donem.ad:
            etkinlik = 66
        elif 'Bahar' in donem.ad:
            etkinlik = 67
        else:
            etkinlik = 68

        # Kapsanan donemin ders baslangic tarihi
        ders_bas_tarih = Takvim.objects.get(akademik_takvim=akademik_takvim_list[j],
                                            etkinlik=etkinlik).baslangic.date()

        # Kapsanan donemin ders bitis tarihi
        ders_bit_tarih = Takvim.objects.get(akademik_takvim=akademik_takvim_list[j],
                                            etkinlik=etkinlik).bitis.date()

        # Seçilen ayın ilk günü = 01.08.2016
        ay_baslangic = date(yil, ay, 01)

        # Seçilen ayın son günü = 31.08.2016
        ay_bitis = date(yil, ay, takvim[1])

        # 08.08.2016 > 01.08.2016
        # baslangic_tarih = 08.08.2016
        # dönem başlangıcı ve ders başlangıcı seçilen ayın içindedir
        if ders_bas_tarih > ay_baslangic and ders_bas_tarih.month == ay:
            baslangic_tarih = ders_bas_tarih

        # 05.09.2016 > 01.08.2016
        # baslangic_tarih = 31.08.2016
        # dönem başlangıcı seçilen ayın içindedir ama ders başlangıcı diğer aya sarkmıştır
        elif ders_bas_tarih > ay_baslangic and ders_bas_tarih.month != ay:
            baslangic_tarih = ay_bitis

        # 15.07.2016 < 01.08.2016
        # baslangic_tarih = 01.08.2016
        # dönem başlangıcı ve ders başlangıcı seçilen aydan öncedir
        else:
            baslangic_tarih = ay_baslangic

        # 15.08.2016 < 31.08.2016
        # bitis_tarih = 15.08.2016
        # dönem bitişi ve ders bitişi seçilen ayın içindedir
        if ders_bit_tarih < ay_bitis and ders_bit_tarih.month == ay:
            bitis_tarih = ders_bit_tarih

        # 25.07.2016 < 31.08.2016
        # bitis_tarih = 01.08.2016
        # dönem bitişi seçilen ayın içindedir ama ders bitişi bir önceki aydır
        elif ders_bit_tarih < ay_bitis and ders_bit_tarih.month != ay:
            bitis_tarih = ay_baslangic

        # 15.09.2016 > 31.08.2016
        # bitis_tarih = 31.08.2016
        # dönem bitişi ve ders bitişi seçilen aydan sonradır
        else:
            bitis_tarih = ay_bitis

        tarih_araligi.append((baslangic_tarih.day, bitis_tarih.day))

    return tarih_araligi
