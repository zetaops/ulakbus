# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime
from collections import OrderedDict
from ulakbus.models.form import Form, FormData
from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models.personel import Personel, Izin
from zengine import forms
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView
from dateutil.relativedelta import relativedelta
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
    """
        Personel izin işlemlerinin yürütüldüğü CrudView dan türetilmiş classdır.
        Personel Dairesi tarafından işletilmesi düşünülmüş olan izin wf için yazılmıştır.
        Bir personelin tüm izinlerinin görüldüğü ve yeni izinlerin tanımlandığı bir wf dir.
    """
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Izin'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        # object_actions = [
        #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        # ]

    def izin_form(self):
        self.form_out(IzinForm(self.object, current=self.current))

    def goster(self):
        """
            Personelin izin durumunun ve kullandığı izinlerin görüntülendiği metoddur.
        """
        yil = date.today().year
        self.list()
        if "id" in self.current.input:
            self.current.task_data["personel_id"] = self.current.input["id"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        izin_gun = self.hizmet_izin_yil_hesapla(personel)
        kalan_izin = self.kalan_izin_hesapla()
        bu_yil_kalan_izin = str(kalan_izin['yillik'][str(date.today().year)])
        # date.today().year ifadesi int döndürdüğü için bu verinin bir dict key olarak kullanılması için
        # string e dönüştürülmesi gerekir.
        if str(date.today().year-1) in kalan_izin["yillik"]:
            gecen_yil_kalan_izin = str(kalan_izin["yillik"][str(date.today().year-1)])
        else:
            gecen_yil_kalan_izin = "0"
        kalan_mazeret_izin = str(kalan_izin["mazeret"][str(date.today().year)])

        # Personelin izin gün sayısı 365 günden azsa eklemeyi kaldır.
        # Personel pasifse eklemeyi kaldır.
        yil = date.today().year
        izin_hakki_yok_sartlari = [
            izin_gun < 365,
            self.personel_aktif,
            bu_yil_kalan_izin <= 0 and gecen_yil_kalan_izin <= 0 and kalan_mazeret_izin <= 0
        ]
        # Yeni izin butonu için form nesnesi oluşturuluyor.
        _form = JsonForm()
        # Eğer izin hakkı yoksa yeni izin butonu oluşturulmuyor.
        if any(izin_hakki_yok_sartlari):
            _form.yeni_izin_buton = fields.Button("Yeni İzin", cmd="yeni_izin")

        # TODO: Personel bilgileri tabloda gösterilecek
        # Form görüntüleniyor
        self.form_out(_form)
        # Personelin izin hakkı durumunu gösteren tablo oluşturuluyor.
        field_dict = OrderedDict({})
        field_dict["Gün"] = izin_gun
        field_dict["Durum"] = "Aktif" if not personel.arsiv else "Pasif"
        field_dict["%i Yılı Kalan Yıllık İzin"%date.today().year] = bu_yil_kalan_izin
        field_dict["%i Yılı Kalan Yıllık İzin"%(date.today().year-1)] = gecen_yil_kalan_izin
        field_dict["Kalan Mazaret İzni"] = kalan_mazeret_izin
        field_dict["Hizmet Süre"] = izin_gun
        self.output['object'] = {
            "type": "table",
            "fields": field_dict
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

    def gecmis_donem_kullanilan_mazeret_izin(self, personel, baslangic, bitis):
        izinler = Izin.objects.filter(
            personel_id = personel.key,
            tip = 5,
            baslangic__lte = baslangic,
            bitis__gte = bitis
        )
        izin_sayi = 0
        for izin in izinler:
            izin_sayi += (izin.bitis - izin.baslangic).days

        return izin_sayi

    def kalan_izin_hesapla(self):
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        ilk_izin_hakedis = personel.goreve_baslama_tarihi + relativedelta(years=1)
        izinler = Izin.objects.filter(personel_id=personel.key)
        yillik_izinler = dict()
        mazeret_izinler = dict()

        if ilk_izin_hakedis > date.today():
            return {'yillik': None, 'mazeret': None}

        for yil in range(ilk_izin_hakedis.year, date.today().year + 1):

            # Burada içinde bulunulan yılın ilk günü ve son günü arasındaki kayıtları çekmemiz gerekiyor
            # Küçük eşittir yada büyük eşittir şeklinde bir sorgu yapamadığımız için başlangıç tarihi
            # bir önceki yılın son günü, bitiş tarihi ise bir sonraki yılın ilk günü olarak düzenlendi
            baslangic = datetime.strptime("31.12.%s"%(yil-2), "%d.%m.%Y")
            bitis = datetime.strptime("01.01.%s"%(yil), "%d.%m.%Y")
            gecmis_mazeret_izin = self.gecmis_donem_kullanilan_mazeret_izin(personel, baslangic, bitis)
            if (date.today().year - personel.goreve_baslama_tarihi.year) >10:
                yillik_izinler[str(yil)] = 30
            else:
                yillik_izinler[str(yil)] = 20

            if gecmis_mazeret_izin > 10:
                yillik_izinler[str(yil)] -= (gecmis_mazeret_izin - 10)

            mazeret_izinler[str(yil)] = 10

        ara_deger = 0

        for izin in izinler:
            if izin.tip == 1:
                yil = izin.baslangic.year - 1
                if (str(yil) in yillik_izinler.keys()) and (yillik_izinler[str(yil)] > 0):
                    yillik_izinler[str(yil)] -= ((izin.bitis - izin.baslangic).days + 1)
                    if yillik_izinler[str(yil)] < 0:
                        ara_deger = -1*yillik_izinler[str(yil)]
                        yillik_izinler[str(yil)] = 0
                        yillik_izinler[str(yil+1)] -= ara_deger
                else:
                    yil += 1
                    yillik_izinler[str(yil)] -= ((izin.bitis - izin.baslangic).days + 1)
            elif izin.tip == 5:
                mazeret_izinler[str(yil)] -= ((izin.bitis - izin.baslangic).days + 1)


        return {'yillik': yillik_izinler, 'mazeret': mazeret_izinler}

    def kaydet(self):
        """
            Form dan gelen verinin kontrol edilerek uygun olması halinde izin kaydını yapan metoddur
        """
        baslangic_tarih = datetime.strptime(self.current.input["form"]["baslangic"], "%d.%m.%Y")
        bitis_tarih = datetime.strptime(self.current.input["form"]["bitis"], "%d.%m.%Y")
        izin_gun = (bitis_tarih - baslangic_tarih).days

        # Personelin kalan izin günü
        kalan_izin= self.kalan_izin_hesapla()

        # Bilgi mesajları hazırlandı
        mesaj_text = "İzin kaydedildi"
        if (self.current.input["form"]["tip"] == 1) and (kalan_izin["yillik"] < izin_gun):
            mesaj_text = "Yeterli yıllık izin bulunmamaktadır"
            mesaj_type = "error"
        elif (self.current.input["form"] == 5) and (kalan_izin["mazeret"] < izin_gun):
            mesaj_text = "Yeterli mazeret izni bulunamadı"
            mesaj_type = "error"
        else:
            izin_kayit = Izin()
            izin_kayit.tip = self.current.input["form"]["tip"]
            izin_kayit.baslangic = self.current.input["form"]["baslangic"]
            izin_kayit.bitis = self.current.input["form"]["bitis"]
            izin_kayit.onay = self.current.input["form"]["onay"]
            izin_kayit.adres = self.current.input["form"]["adres"]
            izin_kayit.telefon = self.current.input["form"]["telefon"]
            izin_kayit.personel = Personel.objects.get(self.current.task_data["personel_id"])
            izin_kayit.personel_id = str(self.current.task_data["personel_id"])

            # İzin alan personelin yerine vekil bırakması durumu
            if self.current.input["form"]["vekil_id"] != None:
                izin_kayit.vekil = Personel.objects.get(self.current.input["form"]["vekil_id"])
                izin_kayit.vekil_id = str(self.current.input["form"]["vekil_id"])
            izin_kayit.blocking_save()
            mesaj_type = "info"

        self.current.output["msgbox"] = {
            "type" : mesaj_type, "title" : "Terfi Sonuç Bilgisi", "msg" : mesaj_text
        }

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

        izin_turleri = ((1, "Yıllık İzin"), (2, "Mazeret İzni"), (3, "Refakat İzni"),
                        (4, "Fazla Mesai İzni"), (5, "Ücretsiz İzin"))
        gecerli_yil = date.today().year
        yillar = ((gecerli_yil, gecerli_yil),)

        izin_turu = fields.Integer("İzin Türü Seçiniz", choices=izin_turleri)
        izin_ait_yil = fields.Integer("Ait Olduğu Yıl", choices=yillar)
        izin_baslangic = fields.Date("İzin Başlangıç Tarihi")
        izin_bitis = fields.Date("İzin Bitiş Tarihi")
        izin_adres = fields.Text("İzindeki Adres")
        personel_ad_soyad = fields.String("İzin Talep Eden")
        personel_gorev = fields.String("Görevi")
        personel_sicil_no = fields.String("Sicil no")
        personel_birim = fields.String("Birimi")
        yol_izni = fields.Boolean("Yol İzni")
        toplam_izin_gun = fields.Integer("Kullanacağı İzin Süresi(Gün)")
        toplam_kalan_izin = fields.Integer("Kalan İzin Süresi(Gün)")

        ileri = fields.Button("İleri")

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
                'type': 'info', "title": 'İzin Başvuru',
                "msg": '%s yılı için izin kullanımlarınız bitmiştir.' % guncel_yil}
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
                                     title="İzin Talep Formu",
                                     exclude=['personel_ad_soyad', 'personel_gorev',
                                              'toplam_kalan_izin', 'toplam_izin_gun',
                                              'yol_izni', 'personel_birim',
                                              'personel_sicil_no'])

        _form.help_text = """
                          {} yılına ait izinli gün sayınız {}, Kalan gün sayınız {}
                          {} yılına ait izinli gün sayınız {}, Toplam izinli gün sayınız  {}
                          """.format(onceki_yil, onceki_yil_izin[0], onceki_yil_izin[1], guncel_yil, guncel_yil_izin[0],
                                     guncel_yil_izin[1])
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

        msg = {"title": 'İzin Başvurusu Yapıldı',
               "body": '%s %s tarih aralığı için yaptığınız izin talebi başarıyla alınmıştır.' % (
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
            'type': 'info', "title": 'İzin Başvurusu Onaylandı',
            "msg": 'İzin talebi başarıyla onaylanmıştır.'
        }

    def izin_basvuru_goster(self):
        """
        İzin işlemleriyle ilgilenen personel, izin başvurusu yapan personelin izin
        bilgilerini görüntüler.

        """
        form_data = FormData.objects.get(self.current.task_data['izin_form_data_key'])
        _form = self.IzinBasvuruForm(current=self.current,
                                     title="İzin Talep Önizleme Formu",
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
