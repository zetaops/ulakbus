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

import time

from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.auth import Role, AbstractRole, Unit
from ulakbus.models.ogrenci import DegerlendirmeNot, DondurulmusKayit
from ulakbus.models.ogrenci import DonemDanisman
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, Program, Donem, Sube
from ulakbus.models.ogrenci import OgrenciDersi
from ulakbus.models.personel import Personel
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.views.ders.ders import prepare_choices_for_model
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView


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

    Args:
        current: wf current nesnesi

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


class KayitDondurmaForm(forms.JsonForm):
    """
    ``KayitDondurma`` sınıfı için form olarak kullanılacaktır.

    """
    class Meta:
        inline_edit = ['secim', 'aciklama']

    baslangic_tarihi = fields.Date('Kayıt Dondurma Başlangıç Tarihi')

    class Donemler(ListNode):
        secim = fields.Boolean(type="checkbox")
        donem = fields.String('Donem')
        key = fields.String('Key', hidden=True)
        aciklama = fields.String('Aciklama')

    sec = fields.Button("Kaydet")


class OgrenciProgramSecimForm(forms.JsonForm):
    """
    ``OgrenciDersAtama`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button("Seç")


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
        from ulakbus.lib.ogrenci import diploma_no_uret
        try:

            ogrenci_program = OgrenciProgram.objects.get(self.input['form']['program'])
            ogrenci_sinav_list = DegerlendirmeNot.objects.set_params(
                rows=1, sort='sinav_tarihi desc').filter(ogrenci=ogrenci_program.ogrenci)
            ogrenci_son_sinav = ogrenci_sinav_list[0]
            diploma_no = diploma_no_uret(ogrenci_program)
            ogrenci_program.diploma_no = diploma_no
            ogrenci_program.mezuniyet_tarihi = ogrenci_son_sinav.sinav.tarih
            ogrenci_program.save()

            bolum_adi = ogrenci_program.program.bolum_adi
            ogrenci_no = ogrenci_program.ogrenci_no
            ogrenci_adi = '%s %s' % (ogrenci_program.ogrenci.ad, ogrenci_program.ogrenci.soyad)

            self.current.output['msgbox'] = {
                'type': 'info', "title": 'Öğrenci Mezuniyet Kaydı Başarılı',
                "msg": '%s numaralı %s adlı öğrenci %s adlı bölümden %s diploma numarası ile mezun \
                edilmiştir' % (ogrenci_no, ogrenci_adi, bolum_adi, diploma_no)
            }

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Öğrenci Mezuniyet Kaydı Başarısız. Hata Kodu : %s' % e.message
            }


class KayitDondurma(CrudView):
    """Öğrenci Kayıt Dondurma

    Öğrencilerin kayıt donduruma işlemlerinin yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.

    """

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Program Seçim Adımı

        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.

        """
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id

        _form = ProgramSecimForm(current=self.current, title="Öğrenci Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def donem_sec(self):
        baslangic_tarihi = False
        secim_durum = False
        aciklama_metin = ""
        try:
            ogrenci_program = OgrenciProgram.objects.get(self.input['form']['program'])
            self.current.task_data['ogrenci_program_id'] = ogrenci_program.key

            # Öğrenci en fazla 2 dönem için kaydını dondurabilir
            donemler = Donem.objects.set_params(sort='baslangic_tarihi desc', rows='2').filter()
            ogrenci_adi = '%s %s' % (ogrenci_program.ogrenci.ad, ogrenci_program.ogrenci.soyad)

            _form = KayitDondurmaForm(current=self.current, title="Lütfen Dönem Seçiniz")
            for donem in donemler:
                baslangic_tarihi = False
                secim_durum = False
                aciklama_metin = ""
                try:
                    dk = DondurulmusKayit.objects.get(ogrenci_program=ogrenci_program, donem=donem)
                    secim_durum = True
                    aciklama_metin = dk.aciklama
                    baslangic_tarihi = dk.baslangic_tarihi
                except ObjectDoesNotExist:
                    secim_durum = False
                    aciklama_metin = ""

                _form.Donemler(secim=secim_durum, donem=donem.ad, key=donem.key,
                               aciklama=aciklama_metin)

            if baslangic_tarihi:
                _form.baslangic_tarihi = baslangic_tarihi
            else:
                _form.baslangic_tarihi = fields.Date('Başlangıç Tarihi')

            self.form_out(_form)
            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Hata Kodu : %s' % e.message
            }

    def ogrenci_kayit_dondur(self):
        """Öğrenci kayıt dondurma WF son aşamasıdır.

        ``DondurulmusKayit`` modelinde, seçilen her donem başına bir kayıt yaratılır.
        Öğrencinin ilgili program kaydında kayıt_dondurma alanı True olarak değiştirilir,
        Öğrencinin "Öğrenci" olan rolü, "Dondurulmuş Ogrenci" olarak değiştirilir.
        Öğrencinin danışmanına bilgi verilir.

        """
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_id'])
        ogrenci = ogrenci_program.ogrenci
        donemler = self.current.input['form']['Donemler']
        baslangic_tarihi = self.current.input['form']['baslangic_tarihi']
        ogrenci_ad_soyad = "%s %s" % (ogrenci.ad, ogrenci.soyad)
        notify_message = '%s numaralı, %s adlı öğrencinin %s programındaki kaydı ' \
                         'dondurulmuştur' % (ogrenci_program.ogrenci_no, ogrenci_ad_soyad,
                                             ogrenci_program.program.adi)
        for donem in donemler:
            donem_kayit = Donem.objects.get(donem['key'])
            try:

                dk = DondurulmusKayit.objects.get(ogrenci_program=ogrenci_program,
                                                  donem=donem_kayit)
                dk.aciklama = donem['aciklama']
                dk.baslangic_tarihi = baslangic_tarihi
                dk.save()

            except ObjectDoesNotExist:
                dk = DondurulmusKayit()
                dk.ogrenci_program = ogrenci_program
                dk.donem = donem_kayit
                dk.aciklama = donem['aciklama']
                dk.baslangic_tarihi = baslangic_tarihi
                dk.save()

            except Exception as e:

                self.current.output['msgbox'] = {
                    'type': 'warning', "title": 'Bir Hata Oluştu',
                    "msg": 'Hata Kodu : %s' % e.message
                }

            try:
                abstract_role = AbstractRole.objects.get(name="dondurulmus_kayit")
                user = ogrenci.user
                unit = Unit.objects.get(yoksis_no=ogrenci_program.program.yoksis_no)
                current_role = Role.objects.get(user=user, unit=unit)
                current_role.abstract_role = abstract_role
                current_role.save()
            except Exception as e:

                self.current.output['msgbox'] = {
                    'type': 'warning', "title": 'Bir Hata Oluştu',
                    "msg": 'Öğrenci Rol Değişim Kaydı Başarısız. Hata Kodu : %s' % e.message
                }

            # öğrencinin danışmanına bilgilendirme geçilir
            try:
                danisman_key = ogrenci_program.danisman.user.key
                ogrenci_program.danisman.user.send_notification(title="Öğrenci Kaydı Donduruldu",
                                                 message=notify_message, typ=111)
                self.current.output['msgbox'] = {
                    'type': 'info', "title": 'Öğrenci Kayıt Dondurma Başarılı',
                    "msg": '%s' % (notify_message)
                }
            except Exception as e:
                self.current.output['msgbox'] = {
                    'type': 'warning', "title": 'Bir Hata Oluştu',
                    "msg": 'Öğrenci Danışmanı Bilgilendirme Başarısız. Hata Kodu : %s' % (e.message)
                }


class BasariDurum(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def doneme_bazli_not_tablosu(self):

        unit = self.current.role.unit
        program = Program.objects.get(birim=unit)

        ogrenci = self.current.role.get_user().ogrenci
        ogrenci_program = OgrenciProgram.objects.get(program=program,
                                                     ogrenci=ogrenci)
        donemler = [d.donem for d in ogrenci_program.OgrenciDonem]
        donemler = sorted(donemler, key=lambda donem: donem.baslangic_tarihi)
        # donemler = ogrenci_program.tarih_sirasiyla_donemler()

        donem_tablosu = list()

        for donem in donemler:
            donem_basari_durumu = [
                ['Ders Kodu', 'Ders Adi', 'Sinav Notlari', 'Ortalama', 'Durum']
            ]
            ogrenci_dersler = OgrenciDersi.objects.filter(donem=donem,
                                                          ogrenci_program=ogrenci_program)
            dersler = list()
            for d in ogrenci_dersler:
                dersler = list()
                dersler.append(d.ders.kod)
                dersler.append(d.ders_adi())
                degerlendirmeler = DegerlendirmeNot.objects.filter(
                    ogrenci_no=ogrenci_program.ogrenci_no, donem=donem.ad, ders=d.ders)
                notlar = [(d.sinav.get_tur_display(), d.puan) for d in degerlendirmeler]
                if len(notlar) > 0:
                    dersler.append(
                        " - ".join(["**%s:** %s" % (sinav, puan) for sinav, puan in notlar]))
                    notlar = list(zip(*notlar)[1])
                    ortalama = sum(notlar) / len(notlar)
                    dersler.append("{0:.2f}".format(ortalama))
                    dersler.append('Gecti' if ortalama > 50 else 'Kaldi')
                else:
                    dersler.append('')
                    dersler.append('')
                    dersler.append('')
                donem_basari_durumu.append({"fields": dersler})
            donem_tablosu.append(
                {
                    "key": donem.ad,
                    "selected": donem.guncel,
                    "objects": donem_basari_durumu
                }
            )

            self.output['objects'] = donem_tablosu
            self.output['meta']['selective_listing'] = True
            self.output['meta']['selective_listing_label'] = "Dönem Seçiniz"
            self.output['meta']['allow_actions'] = False


class DersSecimForm(forms.JsonForm):
    class Meta:
        inline_edit = ['secim']

    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')

    ileri = fields.Button("İleri")


def ders_arama(current):
    ogrenci = Ogrenci.objects.get(current.session['ogrenci_id'])
    mevcut_subeler = []
    for od in OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=Donem.guncel_donem()):
        mevcut_subeler.append(od.sube)

    q = current.input.get('query')
    r = []

    for o in Sube.objects.search_on(*['ders_adi'], contains=q):
        if o not in mevcut_subeler:
            r.append((o.key, o.__unicode__()))

    current.output['objects'] = r


class OgrenciDersAtama(CrudView):
    """Ögrenci Ders Atama

    Öğrenci Ders atama iş akışı aşağıda tanımlı 4 adımdan oluşur.

    - Program seç:
    Öğrencinin kayıtlı olduğu programlar listelenir ve programlardan biri seçilir.

    - Ders listele:
    Öğrencinin kayıtlı olduğu dersleri listeler. Öğrenciye yeni dersler eklenir.

    - Kontrol:
    Öğrencinin kayıtlı olduğu dersler ve eklenen dersler karşılatırılır.
    Aynı ders key'ine sahip dersler var ise ders_listele iş adımına döner.
    Aynı ders key'ine sahip dersler yok ise ogrenci_ders_kaydet iş akışına gider.

    - Öğrenci Dersi Kaydet:
    Eklenen yeni ders varsa ve bu ders öğrenci dersi olarak kayıtlı değil ise;
    Öğrenciye ait yeni bir ders oluşturulur ve ekrana ders kaydının başarılı olduğuna
    dair mesaj basılır.

    Eklenen ders yok ise;
    Ekrana ders seçimin yapılmadığına ilişkin mesaj yazılır.


    """

    # TODO: Aynı derse ait iki kayıt oluşturulursa farklı renkte görülmeli
    # TODO: quick_add_field ve quick_add_view  class Meta içinde  tanımlanması

    class Meta:
        model = "OgrenciDersi"

    def program_sec(self):
        """
        Öğrencinin kayıtlı olduğu programlar listelenir ve programlardan biri seçilir.

        """
        ogrenci_id = self.current.input['id']
        self.current.session['ogrenci_id'] = ogrenci_id
        _form = OgrenciProgramSecimForm(current=self.current, title="Öğrenci Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def ders_listele(self):
        """
        Öğrencinin kayıtlı olduğu dersleri listeler ve öğrenciye yeni dersler eklenir.

        """

        if 'program_key' and 'dersler' not in self.current.task_data:
            ogrenci_dersi_lst = []
            program_key = self.input['form']['program']
            self.current.task_data['program_key'] = program_key
            guncel_donem = Donem.guncel_donem()
            ogrenci_program = OgrenciProgram.objects.get(program_key)
            ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci_program=ogrenci_program, donem=guncel_donem)
            _form = DersSecimForm(current=self.current, title="Ders Seçiniz")
            for ogrenci_dersi in ogrenci_dersleri:
                ogrenci_dersi_lst.append(ogrenci_dersi.key)
                _form.Dersler(key=ogrenci_dersi.sube.key, ders_adi=ogrenci_dersi.sube.ders_adi)
            self.form_out(_form)
            self.current.task_data['ogrenci_dersi_lst'] = ogrenci_dersi_lst

        else:
            _form = DersSecimForm(current=self.current, title="Ders Seçiniz")
            for ders in self.current.task_data['dersler']:
                try:
                    ogrenci_dersi = OgrenciDersi.objects.get(sube_id=ders['key'],
                                                             ogrenci_id=self.current.session['ogrenci_id'])
                    if ogrenci_dersi.key not in self.current.task_data['ogrenci_dersi_lst']:
                        self.current.task_data['ogrenci_dersi_lst'].append(ogrenci_dersi.key)

                except ObjectDoesNotExist:
                    _form.Dersler(key=ders['key'], ders_adi=ders['ders_adi'])

            for ogrenci_dersi_key in self.current.task_data['ogrenci_dersi_lst']:
                ogrenci_dersi = OgrenciDersi.objects.get(ogrenci_dersi_key)
                _form.Dersler(key=ogrenci_dersi.sube.key, ders_adi=ogrenci_dersi.sube.ders_adi)

            self.form_out(_form)

        self.ders_secim_form_inline_edit()
        self.current.output["meta"]["allow_actions"] = True

    def kontrol(self):
        """
        Öğrencinin kayıtlı olduğu dersler ve eklenen dersler karşılatırılır.
        Aynı ders key'ine sahip dersler var ise ders_listele iş adımına döner.
        Aynı ders key'ine sahip dersler yok ise ogrenci_ders_kaydet iş akışına gider.

        """

        dersler = self.current.input['form']['Dersler']
        self.current.task_data['dersler'] = dersler

        sube_ders_lst = []
        for ders in self.current.input['form']['Dersler']:
            sube = Sube.objects.get(ders['key'])
            sube_ders_lst.append(sube.key)

        for ogrenci_dersi_key in self.current.task_data['ogrenci_dersi_lst']:
            ogrenci_dersi = OgrenciDersi.objects.get(ogrenci_dersi_key)
            if ogrenci_dersi.sube.key not in sube_ders_lst:
                sube_ders_lst.append(ogrenci_dersi.sube.key)

        ders_lst = []
        for sube_key in sube_ders_lst:
            sube = Sube.objects.get(sube_key)
            ders_lst.append(sube.ders.key)

        for item in ders_lst:
            if ders_lst.count(item) > 1:
                self.current.task_data['cmd'] = 'ders_listele'
                break

    def ogrenci_ders_kaydet(self):
        """
        Eklenen yeni ders varsa ve bu ders öğrenci dersi olarak kayıtlı değil ise;
        Öğrenciye ait yeni bir ders oluşturulur ve ekrana ders kaydının başarılı olduğuna
        dair mesaj basılır.

        Eklenen ders yok ise;
        Ekrana ders seçimin yapılmadığına ilişkin mesaj yazılır.

        """

        is_new_lst = []
        for ders in self.current.task_data['dersler']:
            ogrenci_dersi, is_new = OgrenciDersi.objects.get_or_create(sube_id=ders['key'],
                                                                       ogrenci_id=self.current.session['ogrenci_id'])
            is_new_lst.append(is_new)
            if is_new:
                ogrenci_dersi.sube = Sube.objects.get(ders['key'])
                ogrenci_dersi.ogrenci = Ogrenci.objects.get(self.current.session['ogrenci_id'])
                ogrenci_dersi.ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['program_key'])
                ogrenci_dersi.save()

        def all_same(items):
            return all(x == items[0] for x in items)

        if all_same(is_new_lst):
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Öğrenci Ders Ekleme',
                "msg": 'Ders seçimi yapılmadı'
            }
        else:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Öğrenci Ders Ekleme',
                "msg": 'Seçilen ders başarıyla eklendi.'
            }

    def ders_secim_form_inline_edit(self):
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['type'] = 'model'
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['model_name'] = "Ders"
        self.output['forms']['schema']['properties']['Dersler']['quick_add'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add_field'] = "ders_adi"
        self.output['forms']['schema']['properties']['Dersler']['quick_add_view'] = "ders_arama"


class MazeretliDersKaydi(CrudView):
    """Mazeretli ders kaydı yapabilecek öğrencilerin düzenlendiği workflowa ait methodları
    barındıran sınıftır.

    """

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Workflow'un ilk aşamasıdır. Seçilen öğrenciye ait programlar listelenir.

        """
        ogrenci_id = self.current.input['id']
        ogrenci = Ogrenci.objects.get(ogrenci_id)
        _form = forms.JsonForm(current=self.current,
                               title="Öğrenci Programı Seçiniz")
        _form.program = fields.Integer("Öğrenci Programı Seçiniz",
                                       choices=prepare_choices_for_model(OgrenciProgram,
                                                                         ogrenci=ogrenci))
        _form.sec = fields.Button("İleri")
        self.form_out(_form)

    def karar_no_gir(self):
        """Mazeretli öğrenci kaydı, fakülte yönetim kurulu kararıyla yapılmaktadır. Bu adımda
        kullanıcıdan ilgili karar numarasını girmesi beklenir.
        Bu method seçilen öğrencinin ilgili programdaki durumunun ders kaydı yapabilir olup
        olmadığını kontrol eder. Ders kaydı yapabilir durumdaki öğrenciler aktif veya gelen öğrenci
        statüsüne sahip olmalıdırlar.

        """
        aktif_ogrenci_status_list = [1, 12, 14, 16, 18, 20]

        self.current.task_data['program'] = self.current.input['form']['program']
        ogrenci_program = OgrenciProgram.objects.get(self.current.input['form']['program'])

        if ogrenci_program.ogrencilik_statusu in aktif_ogrenci_status_list:
            _form = forms.JsonForm(current=self.current,
                                   title="Fakülte Yönetim Kurulu Karar No Giriniz")
            _form.karar_no = fields.String(title="Fakülte Yönetim Kurulu Karar No")
            _form.sec = fields.Button("Kaydet")
            self.form_out(_form)
        else:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Öğrenci Ders Kaydı Yapamaz',
                "msg": 'Öğrenci Durum Kodu Ders Kaydı İçin Uygun Değil'
            }

    def kaydet(self):
        """Öğrenci Programında ogrenci_ders_kayit_status field'ı mazeretli olarak güncelleyen method.
        TODO: Fakülte Yönetim Kurulu Karar No Loglanacak
        """
        try:
            ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['program'])
            ogrenci_program.ogrenci_ders_kayit_status = 1
            ogrenci_program.save()
        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Öğrenci Ders Kayıt Durumu Değiştirme Başarısız. Hata Kodu : %s' % (
                    e.message)
            }

    def kayit_bilgisi_ver(self):
        """Workflow'n son aşamasıdır. Bu method ile başarılı işlem sonucu kullanıcıya gösterilir.

        """
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['program'])
        ogrenci = ogrenci_program.ogrenci
        ogrenci_ad_soyad = ogrenci.ad + " " + ogrenci.soyad
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Öğrenci Ders Kayıt Durumu Değiştirme Başarılı',
            "msg": '%s nolu %s adlı Öğrencinin %s Programına Ait Ders Kayıt Durumu "Mazeretli" Olarak Güncellendi' % (
                ogrenci_program.ogrenci_no, ogrenci_ad_soyad, ogrenci_program.program.adi)
        }
