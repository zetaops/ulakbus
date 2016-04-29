# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import Program, Ders, Donem
from datetime import date


class SecilenDersForm(JsonForm):
    class Meta:
        include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati',
                   'ects_kredisi', 'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci']

        # read-only feature eklenmesi


class SecilenDersForm2(JsonForm):
    class Meta:
        include = ['ad', 'kod', 'ogrenme_ciktilari', 'ders_icerigi', 'ders_kategorisi',
                   'ders_kaynaklari', 'ders_mufredati', 'verilis_bicimi', 'katilim_sarti', 'yil',
                   'ders_koordinatoru', 'yerine_ders', 'program_donemi']


class DersDuzenle(CrudView):
    class Meta:
        model = "Ders"

    def ders_bilgileri_duzenle_ilk_form(self):
        secilen_ders = self.current.task_data["secilenler"][0]
        ders = Ders.objects.get(key=secilen_ders['key'])
        _form = SecilenDersForm(ders, current=self.current, title="Bu Ders İçin Gereken Değişiklikleri Yapınız")
        _form.help_text = "Kalan Ders Sayisi: %d/%d" % ((len(self.current.task_data["secilen_kontrol"]) -
                                                         (len(self.current.task_data["secilenler"]) - 1))
                                                        , len(self.current.task_data["secilen_kontrol"]))
        _form.kaydet = fields.Button("İkinci Sayfaya Geç")
        self.form_out(_form)

    def ders_bilgileri_duzenle_ilk_form_kaydet(self):
        self.set_form_data_to_object()
        self.object.save()

    def ders_bilgileri_duzenle_ikinci_form(self):
        secilen_ders = self.current.task_data["secilenler"][0]
        ders = Ders.objects.get(key=secilen_ders['key'])
        _form = SecilenDersForm2(ders, current=self.current, title="Bu Ders İçin Gereken Değişiklikleri Yapınız")
        _form.help_text = "Kalan Ders Sayısı: %d/%d" % ((len(self.current.task_data["secilen_kontrol"]) -
                                                         (len(self.current.task_data["secilenler"]) - 1))
                                                        , len(self.current.task_data["secilen_kontrol"]))
        _form.kaydet = fields.Button("Kaydet")
        self.form_out(_form)

    def ders_bilgileri_duzenle_ikinci_form_kaydet(self):
        self.set_form_data_to_object()
        self.object.save()
        del self.current.task_data["secilenler"][0]
        self.current.task_data["ders_duzenle_ekranina_geri_don"] = False
        if len(self.current.task_data["secilenler"]) > 0:
            self.current.task_data["ders_duzenle_ekranina_geri_don"] = True
        else:
            del self.current.task_data["secilenler"]


def program_versiyon_no_uret(senato_karar_no):
    senato_karar_no = "SEN" + str(senato_karar_no)

    """
    Girilen senato numarasının başına "SEN" eklenerek program versiyon numarası üretilir.
    """

    return senato_karar_no


class ProgramDersForm(JsonForm):
    class Dersler(ListNode):
        secim = fields.Boolean(type="checkbox")
        ad = fields.String("Ad", index=True)
        kod = fields.String("Kod", index=True)
        key = fields.String('Key', hidden=True)

    class Meta:
        inline_edit = ['secim']


class ProgramKopyalama(CrudView):
    class Meta:
        model = "Ders"

    def program_sec(self):

        _form = JsonForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
        _choices = prepare_choices_for_model(Program)
        _form.program = fields.Integer(choices=_choices)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

    def senato_no_gir(self):
        self.current.task_data['program_id'] = self.current.input['form']['program']
        _form = JsonForm(current=self.current, title="Senato Numarasi Giriniz")
        _form.senato_karar_no = fields.String("Senato Karar Numarası", index=True)
        _form.kaydet = fields.Button("Kaydet")
        self.form_out(_form)

    def senato_no_kaydet_ders_kopyala(self):

        senato_karar_no = self.current.input['form']['senato_karar_no']
        program_versiyon = program_versiyon_no_uret(senato_karar_no)

        program = Program.objects.get(self.current.task_data['program_id'])
        program.Version.add(senato_karar_no=senato_karar_no, no=program_versiyon)
        program.save()

        guncel_yil = date.today().year
        bir_onceki_yil = str(guncel_yil - 1)
        guncel_yil = str(guncel_yil)

        # todo: ders kopyalama islemi tek sefer yapilmali, bu islem bir servis olarak yazilmali.

        if len(Ders.objects.filter(program=program, yil=guncel_yil)) == 0:
            for ders in Ders.objects.filter(program=program, yil=bir_onceki_yil):
                ders.key = None
                ders.donem = Donem.guncel_donem()
                ders.program_versiyon = program_versiyon
                ders.yil = guncel_yil
                ders.save()

    def ders_tablo(self):

        program = Program.objects.get(self.current.task_data['program_id'])
        guncel_yil = date.today().year
        guncel_yil = str(guncel_yil)

        try:
            _form = ProgramDersForm(current=self.current, title="Değişiklik Yapmak İstediğiniz Dersleri Seçiniz")
            program_dersleri = Ders.objects.filter(program=program, yil=guncel_yil)

            for ders in program_dersleri:
                _form.Dersler(secim=False, kod=ders.kod, ad=ders.ad, key=ders.key)
            _form.duzenle = fields.Button("Onayla")
            self.form_out(_form)

            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Program Dersleri Listeleme Başarısız. Hata Kodu : %s' % e.message
            }

    def ders_tablo_kontrol(self):
        self.current.task_data["dersler"] = self.current.input['form']['Dersler']
        secilen_dersler = []
        for secilen_ders in self.current.task_data["dersler"]:
            if secilen_ders['secim'] == True:
                secilen_dersler.append(secilen_ders)

        self.current.task_data["secilenler"] = secilen_dersler
        self.current.task_data["secilen_kontrol"] = secilen_dersler
        self.current.task_data["ders_duzenleme_ekranina_git"] = False

        if len(self.current.task_data["secilenler"]) > 0:
            self.current.task_data["ders_duzenleme_ekranina_git"] = True

    def degisiklik_bitirme_kontrol(self):
        _form = JsonForm(current=self.current, title="Uyarı Mesajı")

        if self.current.task_data["ders_duzenleme_ekranina_git"] == False:
            _form.help_text = "Değişiklik yapmak için ders seçmelisiniz! Değişiklik yapmadan " \
                              "devam etmek istiyorsanız 'Tamamla' butonuna tıklayınız."

        elif self.current.task_data["ders_duzenle_ekranina_geri_don"] == False:
            _form.help_text = "Değişiklikleriniz kaydedildi. " \
                              "Ders seçme ekranına geri dönmek için 'Geri Dön' butonuna, işleminizi bitirmek için" \
                              " 'Tamamla' butonuna tıklayınız."
            _form.title = "Onay Mesajı"

        _form.geri_don = fields.Button("Ders Seçme Ekranına Geri Dön", flow="ders_tablo")
        _form.onayla = fields.Button("Tamamla", flow="personel_bilgilendir")
        self.form_out(_form)
        del self.current.task_data["dersler"]

    def personel_bilgilendir(self):

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Onay Mesajı',
            "msg": ' Değişiklikleriniz kaydedildi ve program dersleri başarıyla kopyalandı.'
        }
