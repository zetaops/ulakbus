# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.models.ogrenci import Okutman, Donem, Takvim
from ulakbus.lib.personel import personel_izin_gunlerini_getir
from ulakbus.models.ders_sinav_programi import DersEtkinligi
from datetime import datetime, date
from collections import OrderedDict
from ulakbus.lib.date_time_helper import AYLAR, ay_listele, resmi_tatil_gunleri_getir
from ulakbus.lib.common import get_akademik_takvim
from ulakbus.lib.date_time_helper import yil_ve_aya_gore_ilk_ve_son_gun
from zengine.lib.translation import gettext as _, gettext_lazy

guncel_yil = datetime.now().year
guncel_ay = datetime.now().month

# Guncel donem ve 5 onceki yili tuple halinde YIL listesinde tutar.
yil_secenekleri = [(yil, yil) for yil in range(guncel_yil, guncel_yil - 6, -1)]


class TarihForm(JsonForm):
    """
    Puantaj tablosu hazırlanırken ay ve yıl seçiminde
    kullanılan form.
    """

    yil_sec = fields.String(gettext_lazy(u'Yıl Seçiniz'), choices=yil_secenekleri,
                            default=guncel_yil)
    ay_sec = fields.String(gettext_lazy(u'Ay Seçiniz'), choices=ay_listele, default=guncel_ay)


class OkutmanListelemeForm(JsonForm):
    """
    Puantaj tablosu hazırlanacak olan okutmanların listesini
    gösteren form.
    """

    class Meta:
        inline_edit = ['secim']
        allow_add_listnode = False

    class OkutmanListesi(ListNode):
        secim = fields.Boolean(gettext_lazy(u"Seçim"), type="checkbox")
        okutman = fields.String(gettext_lazy(u'Okutman'))
        key = fields.String(hidden=True)


class PuantajFormu(JsonForm):
    class Meta:
        help_text = """
                     R: Resmi Tatil
                     İ: İzinli"""

    pdf_sec = fields.Button("Pdf Çıkar")


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
        _form.title = _(u'Puantaj Tablosu Hazırlamak İstediğiniz Yıl ve Ayı Seçiniz')
        _form.sec = fields.Button(_(u"İlerle"))
        self.form_out(_form)

    def donem_kontrol(self):
        """
        Seçilen ay ve yıla ait dönem olup olmadığını kontrol eder.
        """
        secilen_ay = self.input['form']['ay_sec']
        self.current.task_data["yil"] = self.input['form']['yil_sec']
        self.current.task_data["ay"] = secilen_ay

        # guncel olan ayın ismi getirilir.
        self.current.task_data["ay_isim"] = dict(AYLAR).get(secilen_ay)

        # TODO: aktif donem ve oncesine rastlayan donem varmi diye kontrol etmeliyiz.
        donem_list = Donem.takvim_ayina_rastlayan_donemler(self.current.task_data["yil"],
                                                           self.current.task_data["ay"])

        self.current.task_data['donem_sayi'] = True if donem_list else False

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
        _form.iptal = fields.Button(_(u"İptal"), flow='islem_iptali_bilgilendir')
        self.form_out(_form)

    def islem_iptali_bilgilendir(self):

        """
        İşlem iptal edildiğinde kullanıcı iptal hakkında bilgilendirilir.
        """

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Durum Mesajı'),
            "msg": _(u'Puantaj cetveli görüntüleme işleminiz iptal edilmiştir.')
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
        _form = OkutmanListelemeForm(current=self.current, title=_(u"Okutman Seçiniz"))

        # TODO: ilgili doneme ait okutmanlar listelenmeli.
        okutmanlar = [o for o in Okutman.objects for gorev_birimi in o.GorevBirimi
                      if gorev_birimi.yoksis_no == birim_no and gorev_birimi.donem.key
                      == Donem.guncel_donem(self.current).key]

        for okutman in okutmanlar:
            _form.OkutmanListesi(secim=True, okutman=okutman.__unicode__(), key=okutman.key)

        _form.sec = fields.Button(_(u"İlerle"))
        self.form_out(_form)

    def okutman_secim_kontrol(self):

        """
        İşlem yapılacak öğretim görevlisi seçilip seçilmediğini kontrol eder.
        """
        secilen_okutmanlar = []
        for okutman_secim in self.current.input['form']['OkutmanListesi']:
            if okutman_secim['secim']:
                secilen_okutmanlar.append(okutman_secim)

        self.current.task_data["secilen_okutmanlar"] = secilen_okutmanlar
        self.current.task_data["title"] = self.current.role.unit.name.upper()

        self.current.task_data["okutman_kontrol"] = True if secilen_okutmanlar else False

    def okutman_secim_uyari(self):

        """
        Hiç öğretim görevlisi seçilmediği durumda, uyarı verir.
        """

        _form = JsonForm(current=self.current, title=_(u"Öğretim Görevlisi Seçmelisiniz"))
        _form.help_text = _(u"""İşlem yapabilmek için en az bir öğretim görevlisi seçmelisiniz.
                                Öğretim görevlisi seçimine geri dönmek için Geri Dön butonuna,
                                işlemi iptal etmek için İptal butonuna basabilirsiniz.""")
        _form.geri_don = fields.Button(_(u"Geri Dön"), flow='okutman_sec')
        _form.iptal = fields.Button(_(u"İptal"), flow='islem_iptali_bilgilendir')
        self.form_out(_form)

    def ders_saati_turu_secme(self):
        """
        Ders Ücreti ya da Ek Ders Ücreti hesaplarından birini seçmeye yarar.
        """

        _form = JsonForm(current=self.current, title=_(u"Puantaj Tablosu Hesaplama Türü Seçiniz"))
        _form.ders = fields.Button(_(u"Ders Ücreti Hesapla"), cmd='ders_ucreti_hesapla')
        _form.ek_ders = fields.Button(_(u"Ek Ders Ücreti Hesapla"), cmd='ek_ders_ucreti_hesapla')
        self.form_out(_form)

    def ucret_hesapla(self):
        """
        Seçilen ay ve yıla göre, seçilen her bir öğretim elemanının
        resmi tatil ve izinleri dikkate alarak aylık ders saati planlamasını
        yapar
        """
        # Ders seçim türüne göre ayarlamalar yapılır.
        ek_ders, ders_turu = (True, 'Ek') if self.input['form']['ek_ders'] == 1 else (False, '')

        yil = self.current.task_data["yil"]  # girilen yil
        ay = self.current.task_data["ay"]  # girilen ayin orderi
        ay_isim = self.current.task_data["ay_isim"]  # ayin adi

        # verilen ayın son gunu bulunur 28,31 gibi
        ilk, son = yil_ve_aya_gore_ilk_ve_son_gun(yil, ay)
        ayin_son_gunu = son.day

        birim_unit = self.current.role.unit

        # Secilen ay hangi donemleri kapsiyor, kac donemi kapsıyorsa
        # o donemleri dondürür.
        donem_list = Donem.takvim_ayina_rastlayan_donemler(yil, ay)

        # Resmi tatillerin gununu (23, 12, 8) gibi döndürür.
        resmi_tatil_list = resmi_tatil_gunleri_getir(birim_unit, yil, ay)

        # Kapsadığı dönemlere göre ders baslangıc ve bitis tarihlerini
        # baz alarak kapsadığı her bir dönemin seçilen ayda hangi gün
        # aralıklarını kapsadığı bilgisini tuple olarak dondurur. Bir
        # dönemi kapsıyorsa bir tuple, iki dönemi kapsıyorsa iki tuple
        # döner. (1,12) (19,31) gibi
        tarih_araligi = ders_etkinligine_gore_tarih_araligi(donem_list, yil, ay, birim_unit)

        table_head = ['Öğretim Elemanı']
        table_head.extend([str(d) for d in range(1, ayin_son_gunu + 1)])
        table_head.append('Toplam')

        self.output['objects'] = [table_head]

        # Seçilen okutmanların bulunmaması demek,
        title = _(u"%(baslik)s %(yil)s-%(ay)s AYI %(ders)s DERS PUANTAJ TABLOSU") % {
            'baslik': self.current.task_data["title"],
            'yil': yil,
            'ay': ay_isim.upper(),
            'ders': ders_turu.upper(),
        }

        _form = PuantajFormu(title=title)
        self.form_out(_form)

        for secilen_okutman in self.current.task_data["secilen_okutmanlar"]:
            okutman = Okutman.objects.get(secilen_okutman['key'])

            # Seçilen okutmanın İzin ve Ücretsiz İzinlerini dikkate alarak, verilen ayda
            # hangi günler izinli olduğunu liste halinde döndürmeye yarayan method
            # [17,18,19] gibi
            personel_izin_list = personel_izin_gunlerini_getir(okutman, yil, ay)

            # Verilen döneme ve okutmana göre, haftada hangi gün kaç saat dersi
            # (seçilen seçeneğe göre ders veya ek ders) olduğunu gösteren
            # dictionarylerden oluşan liste, seçilen yıl ve ay bir dönemi kapsıyorsa
            # bir dict, iki dönemi kapsıyorsa iki dict döner.
            ders_etkinlik_list = doneme_gore_okutman_etkinlikleri(donem_list, okutman, ek_ders)

            # Bulunan tarih araliklarina, okutmanın aylık ders etkinliklerine göre
            # ayın hangi gününde dersi varsa kaç saat dersi olduğu bilgisi,
            # izinliyse İ, resmi tatilse R bilgisini bir dictionary e doldurur.
            okutman_aylik_plan, ders_saati = okutman_aylik_plani(donem_list, ders_etkinlik_list,
                                                                 resmi_tatil_list,
                                                                 personel_izin_list,
                                                                 tarih_araligi, yil, ay)

            # Okutmanın oluşturulan bilgilerinin ekrana basılacağı şeklinin oluşturulması
            okutman_bilgi_listesi = okutman_bilgileri_doldur(okutman, ayin_son_gunu,
                                                             okutman_aylik_plan, ders_saati)

            item = {
                "type": "table-multiRow",
                "fields": okutman_bilgi_listesi,
                "actions": False,
            }

            self.output['objects'].append(item)

    def tek_okutman_sec(self):
        okutman = self.current.user.personel.okutman
        self.current.task_data["secilen_okutmanlar"] = [{'key': okutman.key}]
        self.current.task_data["title"] = okutman.__unicode__().upper()


def ders_etkinligine_gore_tarih_araligi(donem_list, yil, ay, birim_unit):
    tarih_araligi = []

    # Hangi dönemin ders başlangıç ve bitiş tarihinin
    # dikkate alınacağını belirlemek için Akademik Takvim'de
    # bulunan etkinlik döneme göre seçilir.

    for donem in donem_list:

        # İçinde bulunulan dönemin ders başlangıç ve bitiş tarihlerini
        # bulmak için kullanılır.

        etkinlik = 66 if 'Güz' in donem.ad else 67 if 'Bahar' in donem.ad else 68

        # Kapsanan donemin ders baslangic tarihi
        akademik_takvim = get_akademik_takvim(birim_unit, donem.ogretim_yili)
        ders_bas_tarih = Takvim.objects.get(akademik_takvim=akademik_takvim,
                                            etkinlik=etkinlik).baslangic.date()

        # Kapsanan donemin ders bitis tarihi
        ders_bit_tarih = Takvim.objects.get(akademik_takvim=akademik_takvim,
                                            etkinlik=etkinlik).bitis.date()

        # Seçilen ayın ilk günü = 01.08.2016
        # Seçilen ayın son günü = 31.08.2016
        ay_baslangic, ay_bitis = yil_ve_aya_gore_ilk_ve_son_gun(yil, ay)

        # 08.08.2016 > 01.08.2016
        # baslangic_tarih = 08.08.2016
        # dönem başlangıcı ve ders başlangıcı seçilen ayın içindedir

        # 05.09.2016 > 01.08.2016
        # baslangic_tarih = 31.08.2016
        # dönem başlangıcı seçilen ayın içindedir ama ders başlangıcı diğer aya sarkmıştır

        # 15.07.2016 < 01.08.2016
        # baslangic_tarih = 01.08.2016
        # dönem başlangıcı ve ders başlangıcı seçilen aydan öncedir

        # 15.08.2016 < 31.08.2016
        # bitis_tarih = 15.08.2016
        # dönem bitişi ve ders bitişi seçilen ayın içindedir

        # 25.07.2016 < 31.08.2016
        # bitis_tarih = 01.08.2016
        # dönem bitişi seçilen ayın içindedir ama ders bitişi bir önceki aydır

        # 15.09.2016 > 31.08.2016
        # bitis_tarih = 31.08.2016
        # dönem bitişi ve ders bitişi seçilen aydan sonradır

        if not ders_bas_tarih > ay_baslangic:
            baslangic_tarih = ay_baslangic.day
        elif ders_bas_tarih.month == ay:
            baslangic_tarih = ders_bas_tarih.day
        else:
            baslangic_tarih = ay_bitis.day

        if not ders_bit_tarih < ay_bitis:
            bitis_tarih = ay_bitis.day
        elif ders_bit_tarih.month == ay:
            bitis_tarih = ders_bit_tarih.day
        else:
            bitis_tarih = ay_baslangic.day

        # Eğer tuple lardan birisi (1,1) ya da (31,31) gibiyse bu
        # seçilen ayın içinde bir döneme rast geldiğini fakat ders etkinliğine
        # rast gelmediğini gösterir, mesela Temmuz ayının seçildiğini varsayarsak
        # yaz dönem başlangıcı 25 Temmuz olsun, ama ders etkinliği 3 Ağustosa sarkmış
        # olsun. Bu durumda ders etkinlikleri seçilen aydan sonraki ayda olduğu için,
        # (31,31) tuple'ı döner, böylelikle hesaplama yapılırken döngünün dönmemesi
        # sağlanmış olur. Hesaplama yapılırken günlerin düzgün hesaplanabilmesi için,
        # tuple'ın ikinci elemanı bir arttırılır. Bunun içinde eğer tuple'ın iki elemanı
        # da eşitse hesaplama yapılırken bir arttırılacağından burada ikinci eleman
        # bir azaltılır.
        if baslangic_tarih == bitis_tarih:
            bitis_tarih -= 1
        tarih_araligi.append((baslangic_tarih, bitis_tarih))

    return tarih_araligi


def doneme_gore_okutman_etkinlikleri(donem_list, okutman, ek_ders):
    """
    Verilen dönemde okutmanın hangi günler kaç saat dersi olduğu
    bilgisini list of dict halinde döndürür. Günler 1-7 Pazt-Pazar
    şeklinde belirlenmiştir. Örnek: {1:4, 3:3, 4:2} gibi. Bu
    dict bize okutmanın Pazartesi 4 saat, Çarşamba günü 3 saatlik
    dersi olduğunu gösterir. Bir dönem varsa bir dict iki dönem varsa,
    iki dict dönecektir. [{1:4, 3:3, 4:2}, {2:5, 5:3}]

    Args:
        donem_list (list): donem objeleri listesi
        okutman (Okutman): okutman objesi
        ek_ders (Boolean): etkinlik ek_ders mi?

    Returns:
        (list): hafta gunu ve ders saati sozluk listesi

    """

    # kontrol ders ya da ek ders hesaplamasını gösterir.
    # Eğer kontrol True ise ders, False ise ek ders hesaplanır.

    ders_etkinlik_list = []
    for donem in donem_list:

        okutman_ders_dict = {}

        for etkinlik in DersEtkinligi.objects.filter(donem=donem, okutman=okutman, ek_ders=ek_ders):

            if not etkinlik.gun in okutman_ders_dict:
                okutman_ders_dict[etkinlik.gun] = etkinlik.sure
            else:
                okutman_ders_dict[etkinlik.gun] += etkinlik.sure

        ders_etkinlik_list.append(okutman_ders_dict)

    return ders_etkinlik_list


def okutman_aylik_plani(donem_list, ders_etkinlik_list, resmi_tatil_list, personel_izin_list,
                        tarih_araligi, yil, ay):
    # Tarih aralığı bir tuple olduğu için
    # her bir dönem için o dönemin tarih aralığı
    # dikkate alınır.
    # {1: 'R', 4: 3, 6: 1, 11: 3, 13: 1, 18: 3, 19: 'R', 20: 1, 25: 3, 27: 1}
    ders_saati = 0
    okutman_aylik_plan = {}
    for j, donem in enumerate(donem_list):

        for i in range(tarih_araligi[j][0], tarih_araligi[j][1] + 1):

            hafta_gun = date(yil, ay, i).isoweekday()
            # Eğer gün personel izin listesinde varsa
            if i in personel_izin_list:
                okutman_aylik_plan[i] = 'İ'

            # Eğer gün personel izin listesinde varsa
            elif i in resmi_tatil_list[j]:
                okutman_aylik_plan[i] = 'R'

            # Eğer o gün izinli ya da resmi tatil değilse
            # ve dersi varsa dictin gün keyine kaç saat olduğu
            # value'su eklenir ve ders saati arttırılır.
            elif hafta_gun in ders_etkinlik_list[j]:
                okutman_aylik_plan[i] = ders_etkinlik_list[j][hafta_gun]
                ders_saati += ders_etkinlik_list[j][hafta_gun]

    return okutman_aylik_plan, ders_saati


def okutman_bilgileri_doldur(okutman, ayin_son_gunu, okutman_aylik_plan, ders_saati):
    okutman_bilgi_listesi = OrderedDict({})

    okutman_bilgi_listesi['Öğretim Elemanı'] = okutman.__unicode__()

    for gun in range(1, ayin_son_gunu + 1):
        if gun in okutman_aylik_plan:
            okutman_bilgi_listesi[' ' + str(gun)] = str(okutman_aylik_plan[gun])
        else:
            okutman_bilgi_listesi[' ' + str(gun)] = ' '

    okutman_bilgi_listesi['Toplam'] = str(ders_saati)

    return okutman_bilgi_listesi
