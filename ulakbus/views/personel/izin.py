# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime

from ulakbus.models.form import Form, FormData
from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models.personel import Personel, Izin
from zengine import forms
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy
from collections import OrderedDict
import time


class IzinForm(JsonForm):
    """
        Ücretsiz izin dışındaki izin işlemleri için jsonform dan türetilmiş bir
        form class dır.
    """
    class Meta:
        title = "Personel İzin Form"
        include = ["tip", "baslangic", "bitis", "onay", "adres", "telefon", "vekil"]

    kaydet_buton = fields.Button("Kaydet")


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
        """
         İzin wf nin ilk ekranını gösteren metodddur. Burada personelin yıllık izin ve mazeret izin hakları gösterilir
        """
        if "id" in self.current.input:
            self.current.task_data["personel_id"] = self.current.input["id"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        izinler = Izin.objects.filter(personel=self.current.task_data["personel_id"])
        bu_yil = date.today().year
        gecen_yil = bu_yil - 1

        # arsiv field eğer true ise personel aktif değildir. Aktif olmayan personele de izin yazılamaz.
        if not personel.arsiv:
            field_dict = OrderedDict({})
            field_dict["%i Kalan Yıllık İzin"%bu_yil] = str(personel.bu_yil_kalan_izin)
            field_dict["%i Kalan Yıllık İzin"%gecen_yil] = str(personel.gecen_yil_kalan_izin)
            field_dict["%i Kullanılan Mazeret İzni"%(bu_yil)] = str(personel.mazeret_izin)
            self.output['object'] = {
                "type": "table",
                "fields": field_dict
            }

            # İzin listeleme ekranına geçiş butonları için form oluşturuldu
            _form = JsonForm()
            _form.button = fields.Button("Yeni İzin", cmd="yeni_izin")
            _form.listele_buton = fields.Button("Kullanılan İzinler", cmd="izin_listele")
            self.form_out(_form)
        else:
            self.current.output["msgbox"] = {
                "type" : "error", "title" : "İşlem Gerçekleştirilemiyor !",
                "msg" : "%s %s isimli personel aktif değildir"%(personel.ad, personel.soyad)
            }

    def izin_form(self):
        self.form_out(IzinForm(self.object, current=self.current))

    def kaydet(self):
        baslangic_tarih = datetime.strptime(self.current.input["form"]["baslangic"], "%d.%m.%Y")
        bitis_tarih = datetime.strptime(self.current.input["form"]["bitis"], "%d.%m.%Y")
        izin_sure = (bitis_tarih - baslangic_tarih).days + 1
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        _form = JsonForm()
        _form.button = fields.Button("İzinler Ekranına Geri Dön")

        bir_sonraki_yil = date.today().year + 1

        if (baslangic_tarih.year == bir_sonraki_yil) or (bitis_tarih.year == bir_sonraki_yil):
            self.current.output["msgbox"] = {
                "type" : "error", "title" : "İşlem Gerçekleştirilemiyor !",
                "msg" : "Bir sonraki yıl için izin yazamazsınız"
            }
        else:
            # TODO : personelin bu_yil_kalan_izin ve gecen_yil_kalan_izin fieldları Nonetype ise hata verir. Kontrol edilecek

            # Personelin izin alıp alamayacağının kontrolü için tanımlandı
            izin_kontrol = False
            if self.current.input["form"]["tip"] == 1:
                if (int(personel.gecen_yil_kalan_izin) + int(personel.bu_yil_kalan_izin)) < izin_sure:
                    self.current.output["msgbox"] = {
                        "type" : "error", "title" : "İşlem Gerçekleştirilemiyor !",
                        "msg" : "Yıllık izin yetersiz"
                    }
                else:
                    personel.gecen_yil_kalan_izin -= izin_sure
                    izin_kontrol = True
                    if personel.gecen_yil_kalan_izin < 0:
                        personel.bu_yil_kalan_izin += personel.gecen_yil_kalan_izin
                        personel.gecen_yil_kalan_izin = 0
            elif self.current.input["form"]["tip"] == 5:
                personel.mazeret_izin += izin_sure
                izin_kontrol = True

            if izin_kontrol:
                yeni_izin = Izin()
                yeni_izin.tip = self.current.input["form"]["tip"]
                yeni_izin.baslangic = self.current.input["form"]["baslangic"]
                yeni_izin.bitis = self.current.input["form"]["bitis"]
                yeni_izin.onay = self.current.input["form"]["onay"]
                yeni_izin.adres = self.current.input["form"]["adres"]
                yeni_izin.telefon = self.current.input["form"]["telefon"]
                yeni_izin.personel = personel
                if("vekil" in self.current.input["form"]):
                    vekil_personel = Personel.objects.get(self.current.input["form"]["vekil"])
                    yeni_izin.vekil = vekil_personel

                yeni_izin.blocking_save()

                personel.save()
                self.current.output["msgbox"] = {
                    "type" : "info", "title" : "İşem Gerçekleştirildi !",
                    "msg" : "İzin kaydedildi"
                }

                self.form_out(_form)

    def izin_listele(self):
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        izinler = Izin.objects.filter(
            personel= personel
        )
        izin_list = []
        for izin in izinler:
            izin_dict = OrderedDict({})
            izin_dict["İzin Tip"] = izin.get_tip_display()
            izin_dict["İzin Başlangıç"] = izin.baslangic.strftime("%d.%m.%Y")
            izin_dict["İzin Bitiş"] = izin.bitis.strftime("%d.%m.%Y")
            izin_dict["Onay Tarihi"] = izin.onay.strftime("%d.%m.%Y")
            izin_dict["İzin Süresi/Gün"] = str((izin.bitis - izin.baslangic).days + 1)
            izin_list.append(izin_dict)

        self.output["object"] = {
            "title" : "Personelin Kullandığı İzinler",
            "type" : "table-multiRow",
            "fields" : izin_list
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

        _form.help_text = _(u"""
                          {onceki} yılına ait izinli gün sayınız {onceki_izin}, Kalan gün sayınız {onceki_kalan}
                          {guncel} yılına ait izinli gün sayınız {guncel_izin}, Toplam izinli gün sayınız  {guncel_kalan}
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
        _form.toplam_izin_gun = delta.days
        _form.toplam_kalan_izin = IzinBasvuru.TOPLAM_IZIN_SAYISI - delta.days
        _form.personel_ad_soyad = "%s %s" % (personel.ad, personel.soyad)
        self.form_out(_form)
