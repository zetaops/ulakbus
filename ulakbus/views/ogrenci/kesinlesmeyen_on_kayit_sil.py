# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from pyoko import fields as furkan
from pyoko.exceptions import ObjectDoesNotExist
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import OgrenciProgram, Unit, Program, AkademikTakvim
from datetime import date
import time
from ulakbus.lib.common import get_akademik_takvim


class OnKayitSilForm(JsonForm):
    class Meta:
        inline_edit = ['secim', 'action_secim']

    class SilmeForm(ListNode):
        secim = fields.Boolean("Seçim", type="checkbox")
        birim_ad = fields.String("Ad", hidden=True)
        tanim = fields.String("Tanım", index=True)
        form_sira = fields.Integer("Form Sırası", hidden=True)
        ogrenci_sayisi = fields.Integer("Silinecek Öğrenci Sayısı", index=True)
        action_secim = fields.Boolean("Action Seçim", type="checkbox")
        birim_no = fields.String("Birim No", hidden=True)
        key = fields.String('Key', hidden=True)


class OnKayitSilUyariForm(JsonForm):
    class UyariForm(ListNode):
        birim = fields.String("Birim Adı", index=True)
        ogrenci_ad = fields.String("Öğrenci Adı", index=True)
        ogrenci_soyadi = fields.String("Öğrenci Soyadı", index=True)


class OnKayitSil(CrudView):
    class Meta:
        model = "Unit"

    def on_kayit_silme_tercih_form(self):

        _form = OnKayitSilForm(current=self.current,
                               title="Kaydı Gerçekleşmeyen Ön Kayıt Öğrencilerini Silmek İstediğiniz Birimi Seçiniz")
        parent = Unit.objects.get(parent_unit_no=0)
        birimler = Unit.objects.filter(parent_unit_no=parent.yoksis_no)
        silinecek_ogrenci_sayisi = len(OgrenciProgram.objects.filter(durum=1))

        birim_type = []

        for birim in birimler:
            if not birim.unit_type in birim_type and birim.is_active:
                birim_type.append(birim.unit_type)

        _form.SilmeForm(secim=False, tanim="Üniversite Çapında Tüm Öğrencileri Sil", birim_ad="Üniversite",
                        form_sira=1, ogrenci_sayisi=silinecek_ogrenci_sayisi, action_secim=False)
        silinecek_ogrenci_sayisi = 0
        for type in birim_type:
            if not type in ['İdari', 'Rektörlük', 'Araştırma ve Uygulama Merkezleri']:
                # _form.SilmeForm(secim=False, tanim=type, birim_ad=type, durum=0, form_sira = 1)
                birimler = Unit.objects.filter(unit_type=type)
                for birim in birimler:
                    silinecek_ogrenci_sayisi += len(
                        OgrenciProgram.objects.filter(durum=1, bagli_oldugu_ana_birim=birim))
                _form.SilmeForm(secim=False, tanim=type + " Çapında Tüm Öğrencileri Sil",
                                birim_ad=type, form_sira=2, ogrenci_sayisi=silinecek_ogrenci_sayisi, action_secim=False)
        _form.duzenle = fields.Button("Seçilen Birimleri Sil")
        self.form_out(_form)

    def secilen_birim_kontrol(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        self.current.task_data["secim_kontrol"] = True
        self.current.task_data["secim_var"] = False
        self.current.task_data["action2"] = False
        self.current.task_data["action3"] = False
        self.current.task_data["action4"] = False
        for birim in self.current.task_data["gelen_form"]:
            if birim['secim']:
                self.current.task_data["secim_kontrol"] = False
                self.current.task_data["secim_var"] = True
            if birim['action_secim'] == True and birim['form_sira'] == 2:
                self.current.task_data["action2"] = True
                self.current.task_data["secim_kontrol"] = False
            if birim['action_secim'] == True and birim['form_sira'] == 3:
                self.current.task_data["action3"] = True
                self.current.task_data["secim_kontrol"] = False
            if birim['action_secim'] == True and birim['form_sira'] == 4:
                self.current.task_data["action4"] = True
                self.current.task_data["secim_kontrol"] = False

    def on_kayit_silme_tercih_form_2(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']:
                unit_type = birim['birim_ad']
                # self.current.task_data["secilen_birim"] = unit_type
                # secilen_birim = Unit.objects.filter(unit_type =unit_type)
        secilen_birim = Unit.objects.filter(unit_type=unit_type, is_active=True)

        _form = OnKayitSilForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilen_birim:
            if secilen_alt_birim.is_active:
                silinecek_ogrenci_sayisi = len(OgrenciProgram.objects.filter(durum=1,
                                                                             bagli_oldugu_ana_birim=secilen_alt_birim))
                _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                birim_ad=secilen_alt_birim.name, form_sira=3,
                                key=secilen_alt_birim.key, ogrenci_sayisi=silinecek_ogrenci_sayisi, action_secim=False)

        _form.sec = fields.Button("Seçilen Birimleri Sil")
        self.form_out(_form)

    def on_kayit_silme_tercih_form_3(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']:
                birim_key = birim['key']

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no)
        _form = OnKayitSilForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilenler:
            # if secilen_alt_birim.is_active and len(Program.objects.filter(bolum=secilen_alt_birim))>0:
            if secilen_alt_birim.is_active:
                silinecek_ogrenci_sayisi = 0
                silinecek_ogrenci_sayisi = len(OgrenciProgram.objects.filter(durum=1,
                                                                             bagli_oldugu_bolum=secilen_alt_birim))
                _form.SilmeForm(secim=False,
                                tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                birim_ad=secilen_alt_birim.name, form_sira=4, key=secilen_alt_birim.key,
                                ogrenci_sayisi=silinecek_ogrenci_sayisi, action_secim=False)
        _form.sec = fields.Button("Seçilen Birimleri Sil")
        self.form_out(_form)

    def on_kayit_silme_tercih_form_4(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']:
                birim_key = birim['key']

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no)
        _form = OnKayitSilForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilenler:
            if secilen_alt_birim.is_active:
                try:
                    program = Program.objects.get(yoksis_no=secilen_alt_birim.yoksis_no)
                except:
                    program = secilen_alt_birim

                silinecek_ogrenci_sayisi = len(OgrenciProgram.objects.filter(durum=1, program=program))
                _form.SilmeForm(secim=False,
                                tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                key=secilen_alt_birim.key,
                                birim_ad=secilen_alt_birim.name, form_sira=5, ogrenci_sayisi=silinecek_ogrenci_sayisi
                                , action_secim=False)
        _form.sec = fields.Button("Seçilen Birimleri Sil")
        self.form_out(_form)

    def personel_onay(self):

        self.current.task_data["secilen"] = self.current.input['form']['SilmeForm']
        _form = OnKayitSilUyariForm(current=self.current, title="Onay Mesajı")
        _form.help_text = """Aşağıda gösterilen birim veya birimlerde bulunan
                             öğrencileri silmek üzeresiniz. Bu işlem geri alınamaz!
                             Onaylamak için Tamamla butonuna basınız.
                             İptal edip geri dönmek istiyorsanız İptal butonuna basınız."""

        secilen_birimler = []
        secilen_birim_adi = []
        form_sirasi = []
        self.current.task_data["birim"] = self.current.input['form']['SilmeForm']
        for secilen_birim in self.current.task_data["birim"]:
            if secilen_birim['secim'] == True:
                try:
                    secilen_birimler.append(Unit.objects.get(secilen_birim['key']))
                except:
                    secilen_birim_adi.append(secilen_birim['birim_ad'])

                form_sirasi.append(secilen_birim['form_sira'])
        ogrenci_sayisi = len(form_sirasi)

        if 1 in form_sirasi:
            ogrenciler = OgrenciProgram.objects.filter(durum=1)
            for ogrenci in ogrenciler:
                _form.UyariForm(birim=ogrenci.program.adi, ogrenci_ad=ogrenci.ogrenci.ad,
                                ogrenci_soyadi=ogrenci.ogrenci.soyad)

        else:
            if 2 in form_sirasi:
                for i in range(0, ogrenci_sayisi):
                    birimler = Unit.objects.filter(unit_type=secilen_birim_adi[i])
                    for birim in birimler:
                        ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_ana_birim=birim)
                        for ogrenci in ogrenciler:
                            _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                            ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 3 in form_sirasi:
                for i in range(0, ogrenci_sayisi):
                    ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_ana_birim=secilen_birimler[i])
                    for ogrenci in ogrenciler:
                        _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 4 in form_sirasi:
                for i in range(0, ogrenci_sayisi):
                    ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_bolum=secilen_birimler[i])
                    for ogrenci in ogrenciler:
                        _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 5 in form_sirasi:
                for i in range(0, ogrenci_sayisi):
                    try:
                        program = Program.objects.get(yoksis_no=secilen_birimler[i].yoksis_no)
                    except:
                        program = Unit.objects.get(yoksis_no=secilen_birimler[i].yoksis_no)
                    ogrenciler = OgrenciProgram.objects.filter(program=program)
                    for ogrenci in ogrenciler:
                        _form.UyariForm(birim=ogrenci.program(), ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

        _form.tamamla = fields.Button("Tamamla", flow="kayit_tarihi_kontrol_sil")
        _form.iptal = fields.Button("İptal", flow="on_kayit_silme_tercih_form")
        self.form_out(_form)

    def kayit_tarihi_kontrol_sil(self):

        secilen_birimler = []
        form_sirasi = []
        # self.current.task_data["birim"] = self.current.input['form']['SilmeForm']
        for secilen_birim in self.current.task_data["secilen"]:
            if secilen_birim['secim'] == True:
                secilen_birimler.append(secilen_birim['birim_ad'])
                form_sirasi.append(secilen_birim['form_sira'])

        secilen_birim_sayisi = len(secilen_birimler)

        self.current.task_data["kayit_tarih_kontrol"] = True
        kayit_tarihi_bitmeyenler = []

        if 1 in form_sirasi:
            on_kayit_ogrenciler = OgrenciProgram.objects.filter(durum=1)
            for on_kayit_ogrenci in on_kayit_ogrenciler:
                akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
                son_kayit_tarihi = akademik_birim.Takvim[9].bitis
                if date.today() < son_kayit_tarihi:
                    self.current.task_data["kayit_tarih_kontrol"] = False
                    kayit_tarihi_bitmeyenler.append(akademik_birim.name)
                    # if self.current.task_data["kayit_tarih_kontrol"]:
                    #     on_kayit_ogrenciler.delete()
                    #     on_kayit_ogrenciler.save()

        else:
            if 2 in form_sirasi:
                for i in range(0, secilen_birim_sayisi):
                    birimler = Unit.objects.filter(unit_type=secilen_birimler[i])
                    for birim in birimler:
                        on_kayit_ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_ana_birim=birim)

                for on_kayit_ogrenci in on_kayit_ogrenciler:
                    akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
                    son_kayit_tarihi = akademik_birim.Takvim[9].bitis
                    if date.today() < son_kayit_tarihi:
                        self.current.task_data["kayit_tarih_kontrol"] = False
                        kayit_tarihi_bitmeyenler.append(birim.name)
                        # if self.current.task_data["kayit_tarih_kontrol"]:
                        #     on_kayit_ogrenciler.delete()
                        #     on_kayit_ogrenciler.save()

            if 3 in form_sirasi:
                for i in range(0, secilen_birim_sayisi):
                    on_kayit_ogrenciler = OgrenciProgram.objects.filter(durum=1,
                                                                        bagli_oldugu_ana_birim=secilen_birimler[i])
                    for on_kayit_ogrenci in on_kayit_ogrenciler:
                        akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
                        son_kayit_tarihi = akademik_birim.Takvim[9].bitis
                        if date.today() < son_kayit_tarihi:
                            self.current.task_data["kayit_tarih_kontrol"] = False
                            kayit_tarihi_bitmeyenler.append(birim.name)
                            if self.current.task_data["kayit_tarih_kontrol"]:
                                on_kayit_ogrenciler.delete()
                                on_kayit_ogrenciler.save()

            if 4 in form_sirasi:
                for i in range(0, secilen_birim_sayisi):
                    on_kayit_ogrenciler = OgrenciProgram.objects.filter(durum=1,
                                                                        bagli_oldugu_bolum=secilen_birimler[i])

                    programlar = Program.objects.filter(bolum=secilen_birimler[i])
                    akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
                    son_kayit_tarihi = akademik_birim.Takvim[9].bitis
                    if date.today() < son_kayit_tarihi:
                        self.current.task_data["kayit_tarih_kontrol"] = False
                        kayit_tarihi_bitmeyenler.append(birim.name)
                        # if self.current.task_data["kayit_tarih_kontrol"]:
                        #     for program in programlar:
                        #         OgrenciProgram.objects.filter(durum=1,program=program).delete()
                        #         OgrenciProgram.objects.filter(durum=1, program=program).save()

            if 5 in form_sirasi:
                for i in range(0, secilen_birim_sayisi):
                    program = Program.objects.get(yoksis_no=secilen_birimler[i].yoksis_no)
                    on_kayit_ogrenciler = OgrenciProgram.objects.filter(durum=1,
                                                                        program=program)

                    on_kayit_ogrenciler = OgrenciProgram.objects.filter(durum=1, program=secilen_birimler[i])
                    akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
                    son_kayit_tarihi = akademik_birim.Takvim[9].bitis
                    if date.today() < son_kayit_tarihi:
                        self.current.task_data["kayit_tarih_kontrol"] = False
                        kayit_tarihi_bitmeyenler.append(birim.name)
                        # if self.current.task_data["kayit_tarih_kontrol"]:
                        #     on_kayit_ogrenciler.delete()
                        #     on_kayit_ogrenciler.save()

        self.current.task_data['kayit_tarihi_bitmeyenler'] = kayit_tarihi_bitmeyenler

    def secim_kontrol_uyari(self):
        _form = JsonForm(current=self.current, title="Uyarı Mesajı")
        _form.help_text = """Devam edebilmek için en az bir birim seçmelisiniz.
                             Geriye dönmek için 'Geri Dön' butonuna tıklayınız."""
        _form.geri_don = fields.Button("Geri Dön", flow="on_kayit_silme_tercih_form")
        self.form_out(_form)

    def personel_bilgilendir(self):

        _form = JsonForm(current=self.current, title="Uyarı Mesajı")
        _form.help_text = """Seçilen birimdeki öğrenciler başarıyla silindi."""
        self.form_out(_form)

    def personel_kayit_uyari(self):

        _form = OnKayitSilUyariForm(current=self.current, title="Uyarı Mesajı")
        _form.help_text = """Aşağıdaki birim veya birimlerde kayıt işlemi hala devam etmektedir!
                             Kayıt işlemi bitmeyen birimlerde silme işlemi yapılamaz. Lütfen
                             kayıt işleminin bitmesini bekleyiniz."""
        for bitmeyen_birim in self.current.task_data['kayit_tarihi_bitmeyenler']:
            _form.UyariForm(birim=bitmeyen_birim)

        _form.geri_don = fields.Button("Geri Dön", flow="on_kayit_silme_tercih_form")
        self.form_out(_form)
