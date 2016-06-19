# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.models.ogrenci import OgrenciProgram, Unit, Program
from datetime import date
from ulakbus.lib.common import get_akademik_takvim


class OnKayitSilForm(JsonForm):
    class Meta:
        inline_edit = ['secim', 'action_secim']

    class SilmeForm(ListNode):
        secim = fields.Boolean("Seçim", type="checkbox")
        birim_ad = fields.String("Ad", hidden=True)
        tanim = fields.String("Tanım", index=True)
        form_sira = fields.Integer("Form Sırası", hidden=True)
        # ogrenci_sayisi = fields.Integer("Silinecek Öğrenci Sayısı", index=True)
        action_secim = fields.Boolean("Action Seçim", type="checkbox")
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

        birim_type = []

        for birim in birimler:
            if not birim.unit_type in birim_type and birim.is_active and birim.is_academic:
                birim_type.append(birim.unit_type)

        _form.SilmeForm(secim=False, tanim="Üniversite Çapında Tüm Öğrencileri Sil", birim_ad="Üniversite",
                        form_sira=1, action_secim=False)
        for type in birim_type:
            if not type in ['İdari', 'Rektörlük', 'Araştırma ve Uygulama Merkezleri']:
                _form.SilmeForm(secim=False, tanim=type,
                                birim_ad=type, form_sira=2, action_secim=False)

        _form.duzenle = fields.Button("Seçilen Birimleri Sil")
        self.form_out(_form)

    def on_kayit_silme_tercih_form_2(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']: unit_type = birim['birim_ad']

        secilenler = Unit.objects.filter(unit_type=unit_type, is_active=True)

        form_olustur(secilenler, self, 3)

    def on_kayit_silme_tercih_form_3(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']:
                birim_key = birim['key']

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no, is_active=True)

        form_olustur(secilenler, self, 4)

    def on_kayit_silme_tercih_form_4(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['action_secim']:
                birim_key = birim['key']

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no, is_active=True)
        form_olustur(secilenler, self, 5)

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

    def personel_onay(self):

        _form = OnKayitSilUyariForm(current=self.current, title="Onay Mesajı")
        _form.help_text = """Aşağıda gösterilen kaydı gerçekleşmeyen öğrencileri
                             silmek üzeresiniz. Bu işlem geri alınamaz!
                             Onaylamak için Tamamla butonuna basınız.
                             İptal edip geri dönmek istiyorsanız İptal butonuna basınız."""

        secilen_birimler = []
        secilen_birim_adi = []
        form_sirasi = []
        silinecek_ogrenciler = []
        for secilen_birim in self.current.task_data["gelen_form"]:
            if secilen_birim['secim'] == True:
                try:
                    secilen_birimler.append(Unit.objects.get(secilen_birim['key']))
                except:
                    secilen_birim_adi.append(secilen_birim['birim_ad'])

                form_sirasi.append(secilen_birim['form_sira'])
        secim_sayisi = len(form_sirasi)

        if 1 in form_sirasi:
            ogrenciler = OgrenciProgram.objects.filter(durum=1)
            for ogrenci in ogrenciler:
                silinecek_ogrenciler.append(ogrenci)
                _form.UyariForm(birim=ogrenci.program.adi, ogrenci_ad=ogrenci.ogrenci.ad,
                                ogrenci_soyadi=ogrenci.ogrenci.soyad)

        else:
            if 2 in form_sirasi:
                for i in range(secim_sayisi):
                    birimler = Unit.objects.filter(unit_type=secilen_birim_adi[i])
                    for birim in birimler:
                        ogrenciler = OgrenciProgram.objects.filter(durum=1, bagli_oldugu_ana_birim=birim)
                        for ogrenci in ogrenciler:
                            silinecek_ogrenciler.append(ogrenci)
                            _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                            ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 3 in form_sirasi:
                for i in range(secim_sayisi):
                    ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_ana_birim=secilen_birimler[i])
                    for ogrenci in ogrenciler:
                        silinecek_ogrenciler.append(ogrenci)
                        _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 4 in form_sirasi:
                for i in range(secim_sayisi):
                    ogrenciler = OgrenciProgram.objects.filter(bagli_oldugu_bolum=secilen_birimler[i])
                    for ogrenci in ogrenciler:
                        silinecek_ogrenciler.append(ogrenci)
                        _form.UyariForm(birim=ogrenci.program, ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

            if 5 in form_sirasi:
                for i in range(secim_sayisi):
                    try:
                        program = Program.objects.get(yoksis_no=secilen_birimler[i].yoksis_no)
                    except:
                        program = Unit.objects.get(yoksis_no=secilen_birimler[i].yoksis_no)
                    ogrenciler = OgrenciProgram.objects.filter(program=program)
                    for ogrenci in ogrenciler:
                        silinecek_ogrenciler.append(ogrenci)
                        _form.UyariForm(birim=ogrenci.program(), ogrenci_ad=ogrenci.ogrenci.ad,
                                        ogrenci_soyadi=ogrenci.ogrenci.soyad)

        self.current.task_data['silinecek_ogrenciler'] = silinecek_ogrenciler

        _form.tamamla = fields.Button("Tamamla", flow="kayit_tarihi_kontrol_sil")
        _form.iptal = fields.Button("İptal", flow="on_kayit_silme_tercih_form")
        self.form_out(_form)

    def kayit_tarihi_kontrol_sil(self):

        self.current.task_data["kayit_tarih_kontrol"] = True
        kayit_tarihi_bitmeyenler = []

        for on_kayit_ogrenci in self.current.task_data['silinecek_ogrenciler']:
            akademik_birim = get_akademik_takvim(on_kayit_ogrenci.program.bolum)
            son_kayit_tarihi = akademik_birim.Takvim[9].bitis
            if date.today() < son_kayit_tarihi:
                self.current.task_data["kayit_tarih_kontrol"] = False
                kayit_tarihi_bitmeyenler.append(akademik_birim.name)
            else:
                on_kayit_ogrenci.delete()
                on_kayit_ogrenci.save()

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


def form_olustur(secilenler, self, sira):
    _form = OnKayitSilForm(current=self.current, title="Silinecek Birimi Seçiniz")
    for secilen_alt_birim in secilenler:
        if secilen_alt_birim.is_active:
                _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name + "'nde Bulunan",
                                birim_ad=secilen_alt_birim.name, form_sira=sira,
                                key=secilen_alt_birim.key, action_secim=False)

    _form.sec = fields.Button("Seçilen Birimleri Sil")
    self.form_out(_form)
