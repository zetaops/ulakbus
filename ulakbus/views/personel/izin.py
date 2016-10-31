# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime

from ulakbus.models.form import Form, FormData
from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models.personel import Personel, Izin
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy
import time

class IzinIslemleri(CrudView):
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Izin'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        # object_actions = [
        #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        # ]

    def goster(self):
        yil = date.today().year
        self.list()
        personel = Personel.objects.get(self.input['id'])
        izin_gun = self.hizmet_izin_yil_hesapla(personel)
        kalan_izin = self.kalan_izin_hesapla()
        bu_yil_kalan_izin = getattr(kalan_izin['yillik'], str(yil), 0)
        gecen_yil_kalan_izin = getattr(kalan_izin['yillik'], str(yil - 1), 0)
        kalan_mazeret_izin = getattr(kalan_izin['mazeret'], str(yil), 0)

        # Personelin izin gün sayısı 365 günden azsa eklemeyi kaldır.
        # Personel pasifse eklemeyi kaldır.
        yil = date.today().year
        izin_hakki_yok_sartlari = [
            izin_gun < 365,
            self.personel_aktif,
            bu_yil_kalan_izin <= 0 and gecen_yil_kalan_izin <= 0 and kalan_mazeret_izin <= 0
        ]
        if any(izin_hakki_yok_sartlari):
            self.ListForm.add = None

        # TODO: Personel bilgileri tabloda gösterilecek
        self.output['object'] = {
            "type": "table",
            "fields": [
                {
                    "name": personel.ad,
                    "surname": personel.soyad
                },
                {
                    "gun": izin_gun,
                    "durum": _(u"Aktif") if self.personel_aktif else _(u"Pasif")
                }, {
                    "izinler": kalan_izin,
                    "hizmet_sure": izin_gun
                }
            ]
        }

    def emekli_sandigi_hesapla(self, personel):
        personel_hizmetler = HizmetKayitlari.objects.filter(tckn=personel.tckn)

        baslangic_liste = set()
        bitis_liste = set()

        for hizmet in personel_hizmetler:
            baslangic_liste.add(hizmet.baslama_tarihi)
            bitis_liste.add(hizmet.bitis_tarihi)

        # clean sets any of blank dates
        blank_dates = [date(1900, 1, 1), '']
        for d in blank_dates:
            if d in baslangic_liste:
                baslangic_liste.remove(d)
            if d in bitis_liste:
                bitis_liste.remove(d)

        # sort dates
        baslangic_liste = sorted(baslangic_liste)
        bitis_liste = sorted(bitis_liste)

        if len(baslangic_liste) > 0:
            self.ilk_izin_hakedis = baslangic_liste[0] + timedelta(365)
        else:
            self.ilk_izin_hakedis = date.today()

        toplam_sure = timedelta(0)
        son_baslama = None

        for baslangic in baslangic_liste:
            if son_baslama is None:
                son_baslama = baslangic
            elif len(bitis_liste) > 0 and baslangic >= bitis_liste[0]:
                toplam_sure += bitis_liste[0] - son_baslama
                son_baslama = baslangic
                bitis_liste.remove(bitis_liste[0])

        if son_baslama is None:
            personel_aktif = False
        elif len(bitis_liste) > 0:
            personel_aktif = False
            toplam_sure += bitis_liste[0] - son_baslama
        else:
            personel_aktif = True
            toplam_sure += date.today() - son_baslama

        # print str(int(toplam_sure.days / 360)) + " Yıl, " + str(int(toplam_sure.days % 360)) + " Gün"
        return toplam_sure.days, personel_aktif

    @staticmethod
    def sgk_hesapla(personel):
        personel_birlestirmeler = HizmetBirlestirme.objects.filter(tckn=personel.tckn)
        toplam_gun = 0

        for hizmet in personel_birlestirmeler:
            toplam_gun += hizmet.sure

        return toplam_gun

    def hizmet_izin_yil_hesapla(self, personel):
        emekli_sandigi_gun, aktif = self.emekli_sandigi_hesapla(personel)
        sgk_gun = self.sgk_hesapla(personel)
        self.personel_aktif = aktif
        return emekli_sandigi_gun + sgk_gun

    def kalan_izin_hesapla(self):
        query = self._apply_list_queries(self.object.objects.filter())
        yillik_izinler = dict()
        mazeret_izinler = dict()

        if self.ilk_izin_hakedis > date.today():
            return {'yillik': None, 'mazeret': None}

        for yil in range(self.ilk_izin_hakedis.year, date.today().year + 1):
            yillik_izinler[yil] = 20
            mazeret_izinler[yil] = 10

        for izin in query:
            if izin.tip == 1:
                yil = izin.baslangic.year - 1
                if yil in yillik_izinler.keys() and yillik_izinler[yil] > 0:
                    yillik_izinler[yil] -= (izin.bitis - izin.baslangic).days
                else:
                    yil += 1
                    yillik_izinler[yil] -= (izin.bitis - izin.baslangic).days
            elif izin.tip == 5:
                mazeret_izinler[yil] -= (izin.bitis - izin.baslangic).days

        return {'yillik': yillik_izinler, 'mazeret': mazeret_izinler}


class IzinBasvuru(CrudView):
    """İzin Başvuru İş Akışı

    İzin Başvuru iş akışı dört adımdan ve iki yoldan oluşur.

    İlk yol iki iş akışı adımından oluşur.

    İzin Başvuru Formu Göster:

    İzin başvurusu yaopacak personel için izin başvuru gösterilir.
    Personelin geçen yıl kullandığı izin sayısı, geçen yıldan kalan
    izin sayısı, bu yıl kullandığı izin sayısı, bu yıl kalan izin sayısı
    ve toplamda kalan izin sayısı gösterilir.

    İzin Başvuru Kaydet:

    Personelin izin başvurusu kaydedilir.

    İkinci yol iki iş akışı adımından 2 adımdan oluşur.

    İzin Başvuru Göster:

    İzin işlemleriyle ilgilenen personel, izin başvurusu yapan personelin izin
    bilgilerini görüntüler.

    İzin Başvuru Sonuç Kaydet:

    İzin işlemleriyle ilgilenen personel, izin başvurusu yapan personelin
    iznini kaydeder.

    """
    class Meta:
        model = 'Izin'

    class IzinBasvuruForm(forms.JsonForm):

        """
        İzin Başvuru iş akışı için kullanılacak formdur.

        """

        izin_turleri = ((1, gettext_lazy("Yıllık İzin")),
                        (2, gettext_lazy("Mazeret İzni")),
                        (3, gettext_lazy("Refakat İzni")),
                        (4, gettext_lazy("Fazla Mesai İzni")),
                        (5, gettext_lazy("Ücretsiz İzin")),
        )
        gecerli_yil = date.today().year
        yillar = ((gecerli_yil, gecerli_yil),)

        izin_turu = fields.Integer(gettext_lazy(u"İzin Türü Seçiniz"), choices=izin_turleri)
        izin_ait_yil = fields.Integer(gettext_lazy(u"Ait Olduğu Yıl"), choices=yillar)
        izin_baslangic = fields.Date(gettext_lazy(u"İzin Başlangıç Tarihi"))
        izin_bitis = fields.Date(gettext_lazy(u"İzin Bitiş Tarihi"))
        izin_adres = fields.Text(gettext_lazy(u"İzindeki Adres"))
        personel_ad_soyad = fields.String(gettext_lazy(u"İzin Talep Eden"))
        personel_gorev = fields.String(gettext_lazy(u"Görevi"))
        personel_sicil_no = fields.String(gettext_lazy(u"Sicil no"))
        personel_birim = fields.String(gettext_lazy(u"Birimi"))
        yol_izni = fields.Boolean(gettext_lazy(u"Yol İzni"))
        toplam_izin_gun = fields.Integer(gettext_lazy(u"Kullanacağı İzin Süresi(Gün)"))
        toplam_kalan_izin = fields.Integer(gettext_lazy(u"Kalan İzin Süresi(Gün)"))

        ileri = fields.Button(gettext_lazy(u"İleri"))

    TOPLAM_IZIN_SAYISI = 10

    def izin_kontrol(self):
        self.current.task_data['sicil_no'] = self.current.user.personel.kurum_sicil_no
        lst_form_data = FormData.objects.filter(user_id=self.current.user.key)
        guncel_yil = date.today().year
        onceki_yil = guncel_yil - 1
        onceki_yil_izin_bilgileri = IzinBasvuru.onceki_yil_izinlerini_bul(lst_form_data, onceki_yil)
        guncel_yil_izin_bilgileri = IzinBasvuru.guncel_izinleri_bul(lst_form_data, guncel_yil,
                                                                    onceki_yil_izin_bilgileri[1])
        if guncel_yil_izin_bilgileri[1] <= 0:
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'İzin Başvuru'),
                "msg": _(u'%s yılı için izin kullanımlarınız bitmiştir.') % guncel_yil}
            self.current.task_data['cmd'] = 'end'
        else:
            self.current.task_data['cmd'] = 'izin_basvuru_formu_goster'

    def izin_basvuru_formu_goster(self):
        """
        İzin başvurusu yaopacak personel için izin başvuru gösterilir.
        Personelin geçen yıl kullandığı izin sayısı, geçen yıldan kalan
        izin sayısı, bu yıl kullandığı izin sayısı, bu yıl kalan izin sayısı
        ve toplamda kalan izin sayısı gösterilir.

        """

        personel_id = self.current.user.personel.key
        self.current.task_data['personel_id'] = personel_id
        guncel_yil = date.today().year
        onceki_yil = guncel_yil - 1
        lst_form_data = FormData.objects.filter(user_id=self.current.user.key)
        onceki_yil_izin = IzinBasvuru.onceki_yil_izinlerini_bul(lst_form_data, onceki_yil)
        guncel_yil_izin = IzinBasvuru.guncel_izinleri_bul(lst_form_data, guncel_yil, onceki_yil_izin[1])

        _form = self.IzinBasvuruForm(current=self.current,
                                     title=_(u"İzin Talep Formu"),
                                     exclude=['personel_ad_soyad', 'personel_gorev',
                                              'toplam_kalan_izin', 'toplam_izin_gun',
                                              'yol_izni', 'personel_birim',
                                              'personel_sicil_no'])

        _form.help_text = _(u"""{onceki} yılına ait izinli gün sayınız {onceki_izin}, Kalan gün sayınız {onceki_kalan}
                          {guncel} yılına ait izinli gün sayınız {guncel_izin},Toplam izinli gün sayınız  {guncel_kalan}
                          'dir.
                          """).format(onceki=onceki_yil, onceki_izin=onceki_yil_izin[0], onceki_kalan=onceki_yil_izin[1],
                                      guncel=guncel_yil, guncel_izin=guncel_yil_izin[0], guncel_kalan=guncel_yil_izin[1],
                           )
        self.form_out(_form)

    @staticmethod
    def guncel_izinleri_bul(lst_form_data, guncel_yil, onceki_yil_kalan_izin):
        izinli_gun = 0
        for item in lst_form_data:
            date_format = '%d.%m.%Y'
            a = datetime.strptime(item.data['izin_baslangic'], date_format)
            b = datetime.strptime(item.data['izin_bitis'], date_format)
            if item.data['izin_ait_yil'] == guncel_yil:
                delta = b - a
                izinli_gun += delta.days

        return izinli_gun, (IzinBasvuru.TOPLAM_IZIN_SAYISI - izinli_gun) + onceki_yil_kalan_izin

    @staticmethod
    def onceki_yil_izinlerini_bul(lst_form_data, onceki_yil):
        izinli_gun = 0
        for item in lst_form_data:
            date_format = '%d.%m.%Y'
            # "%Y-%m-%dT%H:%M:%S.000Z"
            if item.data['izin_ait_yil'] == onceki_yil:
                a = datetime.strptime(item.data['izin_baslangic'], date_format)
                b = datetime.strptime(item.data['izin_bitis'], date_format)
                delta = b - a
                izinli_gun += delta.days

        return izinli_gun, IzinBasvuru.TOPLAM_IZIN_SAYISI - izinli_gun

    def izin_basvuru_kaydet(self):
        """
        Personelin izin başvurusu kaydedilir.

        """

        izin_form_data = self.input['form']
        # gereksiz form alanlarını sil
        if 'ileri' in izin_form_data:
            del izin_form_data['ileri']

        self.current.task_data['izin_form_data'] = izin_form_data
        form_personel = Personel.objects.get(self.current.task_data['personel_id'])
        izin_form = Form.objects.get(ad="İzin Formu")
        form_data = FormData()
        form_data.form = izin_form
        form_data.user = form_personel.user
        form_data.data = izin_form_data
        form_data.date = date.today()
        form_data.blocking_save()
        time.sleep(1)
        self.current.task_data['izin_form_data_key'] = form_data.key

        msg = {"title": _(u'İzin Başvurusu Yapıldı'),
               "body": _(u'%s %s tarih aralığı için yaptığınız izin talebi başarıyla alınmıştır.') % (
                   self.input['form']['izin_baslangic'], self.input['form']['izin_bitis'])}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def izin_basvuru_sonuc_kaydet(self):

        """
        İzin işlemleriyle ilgilenen personel, izin başvurusu yapan personelin
        iznini kaydeder.
        TODO : Personele vekalet edecek kişinin seçimi yapılmalı

        """
        from datetime import date
        personel = Personel.objects.get(self.current.task_data['izin_personel_key'])
        form = self.input['form']
        izin = Izin()
        izin.tip = form['izin_turu']
        izin.baslangic = form['izin_baslangic']
        izin.bitis = form['izin_bitis']
        izin.onay = date.today()
        izin.adres = form['izin_adres']
        izin.personel = personel
        izin.save()
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İzin Başvurusu Onaylandı'),
            "msg": _(u'İzin talebi başarıyla onaylanmıştır.')
        }

    def izin_basvuru_goster(self):
        """
        İzin işlemleriyle ilgilenen personel, izin başvurusu yapan personelin izin
        bilgilerini görüntüler.

        """
        form_data = FormData.objects.get(self.current.task_data['izin_form_data_key'])
        _form = self.IzinBasvuruForm(current=self.current,
                                     title=_(u"İzin Talep Önizleme Formu"),
                                     )
        basvuru_data = form_data.data
        personel = form_data.user.personel
        self.current.task_data['izin_personel_key'] = personel.key
        if personel.atama.exist:
            _form.personel_gorev = (personel.atama.kadro.get_unvan_display()
                                    if personel.atama.kadro.exist else None)
            _form.personel_sicil_no = personel.atama.kurum_sicil_no
        if personel.birim.exist:
            _form.personel_birim = personel.birim.name

        date_format = "%d.%m.%Y"
        a = datetime.strptime(basvuru_data['izin_baslangic'], date_format)
        b = datetime.strptime(basvuru_data['izin_bitis'], date_format)
        delta = b - a
        _form.izin_turu = basvuru_data['izin_turu']
        _form.izin_ait_yil = basvuru_data['izin_ait_yil']
        _form.izin_baslangic = basvuru_data['izin_baslangic']
        _form.izin_bitis = basvuru_data['izin_bitis']
        _form.izin_adres = basvuru_data['izin_adres']
        _form.personel_sicil_no = self.current.task_data['sicil_no']
        _form.toplam_izin_gun = delta.days
        _form.toplam_kalan_izin = IzinBasvuru.TOPLAM_IZIN_SAYISI - delta.days
        _form.personel_ad_soyad = "%s %s" % (personel.ad, personel.soyad)
        self.form_out(_form)
