# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Öğrencilerin Genel Bilgileri ile ilgili İş Akışlarına ait
sınıf ve metotları içeren modüldür.

Kimlik Bilgileri, İletişim Bilgileri ve Önceki Eğitim Bilgileri gibi
iş akışlarının yürütülmesini sağlar.

"""

from collections import OrderedDict
from zengine.forms import fields
from zengine import forms
from zengine.views.crud import CrudView
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
<<<<<<< HEAD
<<<<<<< HEAD
=======
from pyoko import LinkProxy
>>>>>>> CHANGE #5056, öğrenci başarı durumuna dönem ağırlıklı ortalama hesabı eklendi
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, Program, Donem, DonemDanisman, DegerlendirmeNot
from ulakbus.models.personel import Personel
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import OgrenciDersi, Sinav
from pyoko.exceptions import ObjectDoesNotExist
=======
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, DegerlendirmeNot
from ulakbus.models.ogrenci import Donem, OgrenciDersi, Sinav
from pyoko.exceptions import ObjectDoesNotExist

>>>>>>> b4fba96a3e03d38c83418fa1c65cf7ad27dfb6d4

class KimlikBilgileriForm(forms.JsonForm):
    """
    ``KimlikBilgileri`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['tckn', "ad", "soyad", "cinsiyet", "dogum_tarihi", "dogum_yeri", "uyruk",
                   "medeni_hali", "baba_adi", "ana_adi",
                   "cuzdan_seri", "cuzdan_seri_no", "kayitli_oldugu_il", "kayitli_oldugu_ilce",
                   "kayitli_oldugu_mahalle_koy",
                   "kayitli_oldugu_cilt_no", "kayitli_oldugu_aile_sıra_no",
                   "kayitli_oldugu_sira_no", "kimlik_cuzdani_verildigi_yer",
                   "kimlik_cuzdani_verilis_nedeni", "kimlik_cuzdani_kayit_no",
                   "kimlik_cuzdani_verilis_tarihi"]

    kaydet = fields.Button("Kaydet", cmd="save")
    mernis_sorgula = fields.Button("Mernis Sorgula", cmd="mernis_sorgula")


class KimlikBilgileri(CrudView):
    """Kimlik Bilgileri İş Akışı

    Kimlik Bilgileri iş akışı 3 adımdan olusmaktadır.

    * Kimlik Bilgileri Formu
    * Mernis Kimlik Sorgulama
    * Kimlik Bilgileri Kaydet

    Bu iş akışımda kullanılan metotlar şu şekildedir:

    Kimlik Bilgilerini Listele:
        CrudView list metodu kullanılmıştır.Kimlik Bilgileri formunu
        listeler.

    Mernis'ten Kimlik Bilgilerini Getir:
        MERNİS, merkezi nüfus idare sisteminin kısa proje adıdır. Bu metot sayesinde
        öğrenciye ait kimlik bilgilerine MERNİS'ten erişilir. KimlikBilgileriForm'undaki
        alanlar MERNİS'ten gelen bilgiler doğrultusunda doldurulur.

    Kaydet:
        MERNİS'ten gelen bilgileri ve yetkili kişinin öğrenciyle girdiği bilgileri
        kaydeder. Bu adım ``CrudView.save()`` metodunu kullanır. İş akışı bu adımdan
        sonra sona erer.

    Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model ``Ogrenci``
    modelidir. Meta.model bu amaçla kullanılmıştır.

    Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "Ogrenci"

    def kimlik_bilgileri(self):
        """Kimlik Bilgileri Formu"""

        self.form_out(KimlikBilgileriForm(self.object, current=self.current))

    def mernis_sorgula(self):
        """Mernis Sorgulama

        Zato wrapper metodlarıyla Mernis servisine bağlanır, servisten dönen
        değerlerle nesneyi doldurup kaydeder.

        """

        servis = MernisKimlikBilgileriGetir(tckn=self.object.tckn)
        kimlik_bilgisi = servis.zato_request()
        self.object(**kimlik_bilgisi)
        self.object.save()


class IletisimBilgileriForm(forms.JsonForm):
    """
    ``İletişimBilgileri`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ["ikamet_il", "ikamet_ilce", "ikamet_adresi", "adres2", "posta_kodu", "e_posta",
                   "e_posta2", "tel_no",
                   "gsm"]

    kaydet = fields.Button("Kaydet", cmd="save")
    kps_sorgula = fields.Button("KPS Sorgula", cmd="kps_sorgula")


class IletisimBilgileri(CrudView):
    """İletişim Bilgileri İş Akışı

   İletişim Bilgileri iş akışı 3 adımdan oluşmaktadır.

   * İletisim Bilgileri Formu
   * KPS Adres Sorgulama
   * Iletisim Bilgileri Kaydet

   Bu iş akışında kullanılan metotlar şu şekildedir.

   İletişim Bilgilerini Listele:
      CrudView list metodu kullanılmıştır. İletişim Bilgileri formunu
      listeler.

   KPS Adres Bilgilerini Getir:
      Bu metot sayesinde öğrenciye ait yerleşim yeri bilgilerine merkezi
      Kimlik Paylaşım Sistemi üzerinden erişilir.

      Iletişim Bilgileri formundaki alanlar KPS'ten gelen bilgiler
      doğrultusunda doldurulur.

    Kaydet:
      KPS'ten gelen bilgileri ya da yetkili kişinin öğrenciyle ilgili girdiği
      bilgileri kaydeder. Bu adım ``CrudView.save()`` metodunu kullanır.
      İş akışı bu adımdan sonra sona erer.

    Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model ``Ogrenci``
    modelidir. Meta.model bu amaçla kullanılmıştır.

    Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "Ogrenci"

    def iletisim_bilgileri(self):
        """İletişim Bilgileri Formu"""

        self.form_out(IletisimBilgileriForm(self.object, current=self.current))

    def kps_sorgula(self):
        """KPS Sorgulama

        Zato wrapper metodlarıyla KPS servisine bağlanır, servisten dönen
        değerlerle nesneyi doldurup kaydeder.

        """
        servis = KPSAdresBilgileriGetir(tckn=self.object.tckn)
        iletisim_bilgisi = servis.zato_request()
        self.object(**iletisim_bilgisi)
        self.object.save()


class OncekiEgitimBilgileriForm(forms.JsonForm):
    """
    ``OncekiEgitimBilgileri`` sınıfı  için object form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ["okul_adi", "diploma_notu", "mezuniyet_yili"]

    kaydet = fields.Button("Kaydet", cmd="save")


class OncekiEgitimBilgileri(CrudView):
    """Önceki Eğitim Bilgileri İş Akışı

   Önceki Eğitim Bilgileri iş akışı 2 adımdan oluşmaktadır.

   * Önceki Eğitim Bilgileri Formu
   * Önceki Eğitim Bilgilerini Kaydet

   Bu iş akışında  kullanılan metotlar şu şekildedir:

   Önceki Eğitim Bilgileri Formunu Listele:
      CrudView list metodu kullanılmıştır. Önceki Eğitim Bilgileri formunu listeler.

   Kaydet:
      Girilen önceki eğitim bilgilerini kaydeder. Bu adım ``CrudView.save()`` metodunu kullanır.
      İş akışı bu adımdan sonra sona erer.

   Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model ``OncekiEgitimBilgisi``
   modelidir. Meta.model bu amaçla kullanılmıştır.

   Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "OncekiEgitimBilgisi"

    def onceki_egitim_bilgileri(self):
        """Önceki Eğitim Bilgileri Formu"""

        self.form_out(OncekiEgitimBilgileriForm(self.object, current=self.current))


def ogrenci_bilgileri(current):
    """Öğrenci Genel Bilgileri

    Öğrenci Genel Bilgileri, öğrencilerin kendi bilgilerini görüntüledikleri
    tek adımlık bir iş akışıdır.

    Bu metod tek adımlık bilgi ekranı hazırlar.

    """

    current.output['client_cmd'] = ['show', ]
    ogrenci = Ogrenci.objects.get(user_id=current.user_id)

    # ordered tablo için OrderedDict kullanılmıştır.
    kimlik_bilgileri = OrderedDict({})
    kimlik_bilgileri.update({'Ad Soyad': "%s %s" % (ogrenci.ad, ogrenci.soyad)})
    kimlik_bilgileri.update({'Cinsiyet': ogrenci.cinsiyet})
    kimlik_bilgileri.update({'Kimlik No': ogrenci.tckn})
    kimlik_bilgileri.update({'Uyruk': ogrenci.tckn})
    kimlik_bilgileri.update({'Doğum Tarihi': '{:%d.%m.%Y}'.format(ogrenci.dogum_tarihi)})
    kimlik_bilgileri.update({'Doğum Yeri': ogrenci.dogum_yeri})
    kimlik_bilgileri.update({'Baba Adı': ogrenci.baba_adi})
    kimlik_bilgileri.update({'Anne Adı': ogrenci.ana_adi})
    kimlik_bilgileri.update({'Medeni Hali': ogrenci.medeni_hali})

    iletisim_bilgileri = {
        'Eposta': ogrenci.e_posta,
        'Telefon': ogrenci.tel_no,
        'Sitem Kullanıcı Adı': current.user.username
    }

    current.output['object'] = [
        {
            "title": "Kimlik Bilgileri",
            "type": "table",
            "fields": kimlik_bilgileri
        },
        {
            "title": "İletişim Bilgileri",
            "type": "table",
            "fields": iletisim_bilgileri
        }
    ]

<<<<<<< HEAD
class ProgramSecimForm(forms.JsonForm):
    """
    ``DanismanAtama`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button("Seç")


class DanismanSecimForm(forms.JsonForm):
    """
    ``DanismanAtama`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button("Kaydet")


class DanismanAtama(CrudView):
    """Danışman Atama

    Öğrencilere danışman atamalarının yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.

    """

def prepare_choices_for_model(model, **kwargs):
    """Model için Seçenekler Hazırla

    Args:
        model: Model
        **kwargs: Keyword argümanları

    Returns:
        Keyword argümanlara göre filtrelenmiş modelin,
        key ve __unicode__ method değerlerini

    """

    return [(m.key, m.__unicode__()) for m in model.objects.filter(**kwargs)]

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Program Seçim Adımı

        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.

        """
        guncel_donem = Donem.objects.filter(guncel=True)[0]
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id
        self.current.task_data['donem_id'] = guncel_donem.key

        _form = ProgramSecimForm(current=self.current, title="Öğrenci Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def danisman_sec(self):
        program_id = self.current.input['form']['program']
        donem_id = self.current.task_data['donem_id']
        self.current.task_data['program_id'] = program_id

        program = OgrenciProgram.objects.get(program_id)

        _form = DanismanSecimForm(current=self.current, title="Danışman Seçiniz")
        _choices = prepare_choices_for_model(DonemDanisman, donem_id=donem_id, bolum=program.program.birim)
        _form.donem_danisman = fields.Integer(choices=_choices)
        self.form_out(_form)

    def danisman_kaydet(self):
        program_id = self.current.task_data['program_id']
        donem_danisman_id = self.input['form']['donem_danisman']

        o = DonemDanisman.objects.get(donem_danisman_id)
        personel = o.okutman.personel

        self.current.task_data['personel_id'] = personel.key

        ogrenci_program = OgrenciProgram.objects.get(program_id)
        ogrenci_program.danisman = personel
        ogrenci_program.save()

    def kayit_bilgisi_ver(self):
        ogrenci_id = self.current.task_data['ogrenci_id']
        personel_id = self.current.task_data['personel_id']

        ogrenci = Ogrenci.objects.get(ogrenci_id)
        personel = Personel.objects.get(personel_id)

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Danışman Ataması Yapıldı',
            "msg": '%s adlı öğrenciye %s adlı personel danışman olarak atandı' % (ogrenci, personel)

class ProgramSecimForm(forms.JsonForm):
    """
    ``DanismanAtama`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button("Seç")


class DanismanSecimForm(forms.JsonForm):
    """
    ``DanismanAtama`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button("Kaydet")


class DanismanAtama(CrudView):
    """Danışman Atama

    Öğrencilere danışman atamalarının yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.

    """

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Program Seçim Adımı

        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.

        """
        guncel_donem = Donem.objects.filter(guncel=True)[0]
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id
        self.current.task_data['donem_id'] = guncel_donem.key

        _form = ProgramSecimForm(current=self.current, title="Öğrenci Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def danisman_sec(self):
        program_id = self.current.input['form']['program']
        donem_id = self.current.task_data['donem_id']
        self.current.task_data['program_id'] = program_id

        program = OgrenciProgram.objects.get(program_id)

        _form = DanismanSecimForm(current=self.current, title="Danışman Seçiniz")
        _choices = prepare_choices_for_model(DonemDanisman, donem_id=donem_id,
                                             bolum=program.program.birim)
        _form.donem_danisman = fields.Integer(choices=_choices)
        self.form_out(_form)

    def danisman_kaydet(self):
        program_id = self.current.task_data['program_id']
        donem_danisman_id = self.input['form']['donem_danisman']

        o = DonemDanisman.objects.get(donem_danisman_id)
        personel = o.okutman.personel

        self.current.task_data['personel_id'] = personel.key

        ogrenci_program = OgrenciProgram.objects.get(program_id)
        ogrenci_program.danisman = personel
        ogrenci_program.save()

    def kayit_bilgisi_ver(self):
        ogrenci_id = self.current.task_data['ogrenci_id']
        personel_id = self.current.task_data['personel_id']

        ogrenci = Ogrenci.objects.get(ogrenci_id)
        personel = Personel.objects.get(personel_id)

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Danışman Ataması Yapıldı',
            "msg": '%s adlı öğrenciye %s adlı personel danışman olarak atandı' % (ogrenci, personel)
        }


class OgrenciMezuniyet(CrudView):
    """Öğrenci Mezuniyet

    Öğrencilerin mezuniyet işlemlerinin yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.

    """

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Program Seçim Adımı

        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.

        """
        guncel_donem = Donem.objects.filter(guncel=True)[0]
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id
        self.current.task_data['donem_id'] = guncel_donem.key

        _form = ProgramSecimForm(current=self.current, title="Öğrenci Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def mezuniyet_kaydet(self):
        from ulakbus.lib.ogrenci import OgrenciHelper
        try:

            mn = OgrenciHelper()
            ogrenci_program = OgrenciProgram.objects.get(self.input['form']['program'])
            ogrenci_sinav_list = DegerlendirmeNot.objects.set_params(
                rows=1, sort='sinav_tarihi desc').filter(ogrenci=ogrenci_program.ogrenci)
            ogrenci_son_sinav = ogrenci_sinav_list[0]
            diploma_no = mn.diploma_notu_uret(ogrenci_program.ogrenci_no)
            ogrenci_program.diploma_no = diploma_no
            ogrenci_program.mezuniyet_tarihi = ogrenci_son_sinav.sinav.tarih
            ogrenci_program.save()

            bolum_adi = ogrenci_program.program.bolum_adi
            ogrenci_no = ogrenci_program.ogrenci_no
            ogrenci_adi = '%s %s' % (ogrenci_program.ogrenci.ad, ogrenci_program.ogrenci.soyad)

            self.current.output['msgbox'] = {
                'type': 'info', "title": 'Bir Hata Oluştu',
                "msg": '%s numaralı %s adlı öğrenci %s adlı bölümden %s diploma numarası ile mezun \
                edilmiştir' % (ogrenci_no, ogrenci_adi, bolum_adi, diploma_no)
            }

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Öğrenci Mezuniyet Kaydı Başarısız. Hata Kodu : %s' % (e.message)
            }
        }
=======
>>>>>>> b4fba96a3e03d38c83418fa1c65cf7ad27dfb6d4

class BasariDurum(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def program_ata(self):
        ogrenci = Ogrenci.objects.get(user = self.current.user)
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci = ogrenci)
        self.current.task_data["ogrenci_program_key"] = ogrenci_program[0].key

    def not_durum(self):
<<<<<<< HEAD
        harflendirme = {
            "AA" : {
                "baslangic" : 90,
                "bitis" : 100,
                "dortluk" : 4.00
            },
            "BA" : {
                "baslangic" : 85,
                "bitis" : 89,
                "dortluk" : 3.50
            },
            "BB" : {
                "baslangic" : 75,
                "bitis" : 84,
                "dortluk" : 3.00
            },
            "CB" : {
                "baslangic" : 70,
                "bitis" : 74,
                "dortluk" : 2.50
            },
            "CC" : {
                "baslangic" : 60,
                "bitis" : 69,
                "dortluk" : 2.00
            },
            "DC" : {
                "baslangic" : 55,
                "bitis" : 59,
                "dortluk" : 1.50
            },
            "DD" : {
                "baslangic" : 50,
                "bitis" : 54,
                "dortluk" : 1.00
            },
            "FD" : {
                "baslangic" : 40,
                "bitis" : 49,
                "dortluk" : 0.50
            },
            "FF" : {
                "baslangic" : 0,
                "bitis" : 39,
                "dortluk" : 0.00
            }
        }
        self.current.output['client_cmd'] = ['show', ]
        donemler = Donem.objects.set_params(sort='baslangic_tarihi desc').filter()
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data["ogrenci_program_key"])
        donemler = ogrenci_program.OgrenciDonem
        donem_sayi = len(donemler)
        for x in range(donem_sayi):
            for y in range(x):
                if donemler[y].donem.baslangic_tarihi > donemler[x].donem.baslangic_tarihi:
                    donem_buffer = donemler[y]
                    donemler[y] = donemler[x]
                    donemler[x] = donem_buffer
        output_array = []
        genel_toplam = 0.0
        self.current.output['client_cmd'] = ['show', ]
        donemler = Donem.objects.set_params(sort='baslangic_tarihi desc').filter()
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data["ogrenci_program_key"])
        output_array = []
        for donem in donemler:
            ogrenci_dersler = OgrenciDersi.objects.filter(
                        ogrenci_program = ogrenci_program,
                        donem = donem
                        )
            for ogrenci_ders in ogrenci_dersler:
                tablo = []
                ders_sinav = {}
                sinavlar = Sinav.objects.filter(ders = ogrenci_ders.ders.ders)
                ders_sinav["Ders"] = ogrenci_ders.ders.ders.ad
                ders_sinav["Ects Kredisi"] = ogrenci_ders.ders.ders.ects_kredisi
                ders_sinav["Yerel Kredisi"] = ogrenci_ders.ders.ders.yerel_kredisi
                for sinav in sinavlar:
                    try:
                        degerlendirme = DegerlendirmeNot.objects.get(sinav = sinav)
                        ders_sinav[sinav.get_tur_display()] = degerlendirme.puan
                    except ObjectDoesNotExist:
                        ders_sinav[sinav.get_tur_display()] = "Sonuçlandırılmadı"

                if type(ogrenci_ders.ortalama) is float:
                    ders_sinav["Ortalama"] = ogrenci_ders.ortalama
                    kredi_toplam += ogrenci_ders.ders.ders.yerel_kredisi
                    agirlikli_not_toplam += ogrenci_ders.ders.ders.yerel_kredisi * harflendirme[ogrenci_ders.harf]["dortluk"]
                if ogrenci_ders.devamsizliktan_kalma:
                    ders_sinav["Harf"] = "F"
                else:
                    if type(ogrenci_ders.ortalama) is float:
                        ders_sinav["Ortalama"] = ogrenci_ders.ortalama
                        for key, value in harflendirme.iteritems():
                            if (ogrenci_ders.ortalama >= value["baslangic"]) & (ogrenci_ders.ortalama <= value["bitis"]):
                                ders_sinav["Harf"] = key
                        kredi_toplam += ogrenci_ders.ders.ders.yerel_kredisi
                        agirlikli_not_toplam += ogrenci_ders.ders.ders.yerel_kredisi * harflendirme[ogrenci_ders.harf]["dortluk"]
                    else:
                        ders_sinav["Ortalama"] = "Sonuçlandırılmadı"
                        ders_sinav["Harf"] = "Sonuçlandırılmadı"                    
                tablo.append(ders_sinav)
            output_array.append({
                    "title"  : "%s Başarı Durumu"%donem.ad,
                    "type"   : "table-multiRow",
                    "fields" : tablo
                })            

        self.output["object"] = output_array
        self.current.ogrenci_program = ogrenci_program[0]
            output_array.append({
                    "title" : "",
                    "type" : "table",
                    "fields" : {
                        "Dönem Ağırlıklı Not Ortalaması" : agirlikli_not_toplam / kredi_toplam
                    }
                })
        ogrenci_dersler = OgrenciDersi.objects.filter(ogrenci_program = ogrenci_program)

        self.output["object"] = output_array