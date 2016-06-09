# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from pyoko import fields as furkan
from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import AkademikTakvim, OgrenciProgram, Unit, Program, User
from datetime import date
import time
from ulakbus.lib.common import get_akademik_takvim


class ProgramDersForm(JsonForm):
    """
    Kopyalanan dersleri tabloda gösterirken kullanılan form.

    """

    class Meta:
        inline_edit = ['secim']

    class SilmeForm(ListNode):
        secim = fields.Boolean("Seçim", type="checkbox")
        birim_ad = fields.String("Ad", hidden=True)
        tanim = fields.String("Tanım", index=True)
        detay = fields.String("Detaylı Birim Seç", index=True)
        durum = fields.Integer("Durum", hidden=True)
        form_sira = fields.Integer("Form Sırası", hidden=True)
        # ogrenci_sayisi = fields.String("Silinecek Öğrenci Sayısı", index=True)
        birim_no = fields.String("Birim No", hidden=True)
        # kod = fields.String("Kod", index=True)
        key = fields.String('Key', hidden=True)


class OnKayitSil(CrudView):
    """Okutman Not Girişi

    Okutmanların öğrenci devamsızlıklarını sisteme girebilmesini
    sağlayan workflowa ait metdodları barındıran sınıftır.

    """

    class Meta:
        model = "Program"

    def on_kayit_silme_tercih_form(self):

        _form = ProgramDersForm(current=self.current,
                                title="Kaydı Gerçekleşmeyen Ön Kayıt Öğrencilerini Silmek İstediğiniz Birimi Seçiniz")
        parent = Unit.objects.get(parent_unit_no=0)
        birimler = Unit.objects.filter(parent_unit_no=parent.yoksis_no)

        birim_type = []

        for birim in birimler:
            if not birim.unit_type in birim_type and birim.is_active:
                birim_type.append(birim.unit_type)

        _form.SilmeForm(secim=False, tanim="Üniversite Çapında Tüm Öğrencileri Sil", birim_ad="Üniversite", durum=0)

        for type in birim_type:
            if not type in ['İdari', 'Rektörlük', 'Araştırma ve Uygulama Merkezleri']:
                # _form.SilmeForm(secim=False, tanim=type, birim_ad=type, durum=0, form_sira = 1)
                _form.SilmeForm(secim=False, tanim=type + " Çapında Tüm Öğrencileri Sil",
                                detay=type + " Seç",
                                birim_ad=type, durum= 0, form_sira=1)
        _form.duzenle = fields.Button("İlerle")
        self.form_out(_form)

    def secilen_birim_kontrol(self):
        self.current.task_data["secilen"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["secilen"]:
            if birim['secim']:
                if birim['durum'] == 1:
                    self.current.task_data["secim_kontrol"] = True
                else:
                    self.current.task_data["secim_kontrol"] = False

    def on_kayit_silme_tercih_form_2(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['secim']:
                unit_type = birim['birim_ad']
                # self.current.task_data["secilen_birim"] = unit_type
                # secilen_birim = Unit.objects.filter(unit_type =unit_type)
        secilen_birim = Unit.objects.filter(unit_type=unit_type, is_active=True)

        _form = ProgramDersForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilen_birim:
            if secilen_alt_birim.is_active:
                # _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name, birim_ad=secilen_alt_birim.name, durum=0,
                #                 form_sira=2, key=secilen_alt_birim.key)
                _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                detay= "Bu Fakülteden Bölüm Seç",
                                birim_ad=secilen_alt_birim.name, durum=0, form_sira=1, key=secilen_alt_birim.key)

        _form.sec = fields.Button("Seç")
        self.form_out(_form)

        # _choices = prepare_choices_for_model(Unit, is_active=True, unit_type=unit_type)
        #
        # _form.program = fields.Integer(choices=_choices)


        # _form = ProgramDersForm(current=self.current,
        #                         title="Kaydı Gerçekleşmeyen Ön Kayıt Öğrencilerini Silmek İstediğiniz Birimi Seçiniz")
        #
        # for birim in secilen_birim:
        #     if birim.is_active:
        #         _form.SilmeForm(secim=False, birim_ad=birim.name)
        # _form.duzenle = fields.Button("Onayla")
        # self.form_out(_form)

    def secilen_birim_kontrol_2(self):
        self.current.task_data["secilen"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["secilen"]:
            if birim['secim']:
                if birim['durum'] == 1:
                    self.current.task_data["secim_kontrol"] = True
                else:
                    self.current.task_data["secim_kontrol"] = False

    def on_kayit_silme_tercih_form_3(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['secim']:
                # unit_type = birim['birim_ad']
                birim_key = birim['key']
                # self.current.task_data["secilen_birim"] = unit_type
                # secilen_birim = Unit.objects.filter(unit_type =unit_type)

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no)
        _form = ProgramDersForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilenler:
            if secilen_alt_birim.is_active:
                # _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name, birim_ad=secilen_alt_birim.name, durum=0,
                #                 form_sira=3, key=secilen_alt_birim.key)
                _form.SilmeForm(secim=False,
                                tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                detay="Bu Bölümden Program Seç",birim_ad=secilen_alt_birim.name, durum=0, form_sira=3, key=secilen_alt_birim.key)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

        # self.current.task_data['birim'] = self.current.input['form']['program']
        # birim = Unit.objects.get(self.current.task_data['birim'])
        #
        # _form = JsonForm(current=self.current, title="Silinecek Birimi Seçiniz")
        # _choices = prepare_choices_for_model(Unit, is_active=True, parent_unit_no=birim.yoksis_no)
        #
        # _form.program = fields.Integer(choices=_choices)
        # _form.sec = fields.Button("Seç")
        # self.form_out(_form)

    def secilen_birim_kontrol_3(self):
        self.current.task_data["secilen"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["secilen"]:
            if birim['secim']:
                if birim['durum'] == 1:
                    self.current.task_data["secim_kontrol"] = True
                else:
                    self.current.task_data["secim_kontrol"] = False

    def on_kayit_silme_tercih_form_4(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['secim']:
                # unit_type = birim['birim_ad']
                birim_key = birim['key']
                # self.current.task_data["secilen_birim"] = unit_type
                # secilen_birim = Unit.objects.filter(unit_type =unit_type)

        secilen_birim = Unit.objects.get(birim_key)

        secilenler = Unit.objects.filter(parent_unit_no=secilen_birim.yoksis_no)
        _form = ProgramDersForm(current=self.current, title="Silinecek Birimi Seçiniz")
        for secilen_alt_birim in secilenler:
            if secilen_alt_birim.is_active:
                # _form.SilmeForm(secim=False, tanim=secilen_alt_birim.name, birim_ad=secilen_alt_birim.name, durum=0,
                #                 form_sira=3, key=secilen_alt_birim.key)
                _form.SilmeForm(secim=False,
                                tanim=secilen_alt_birim.name + "'nde Bulunan Tüm Öğrencileri Sil",
                                birim_ad=secilen_alt_birim.name, durum=0, form_sira=3)
        _form.sec = fields.Button("Onayla")
        self.form_out(_form)


        # self.current.task_data['birim_id'] = self.current.input['form']['program']
        # birim = Unit.objects.get(self.current.task_data['birim_id'])
        #
        # _form = ProgramDersForm(current=self.current,
        #                         title="Kaydı Gerçekleşmeyen Seçiniz")
        #
        # birimler = Unit.objects.filter(parent_unit_no=birim.yoksis_no)
        # for birim in birimler:
        #     _form.SilmeForm(secim=False, tanim=birim.name, birim_ad=birim.name, durum=0)
        #
        # _form.duzenle = fields.Button("İlerle")
        # self.form_out(_form)



        # _form = JsonForm(current=self.current, title="Silinecek Birimi Seçiniz")
        # _choices = prepare_choices_for_model(Unit, is_active=True, parent_unit_no=birim.yoksis_no)
        #
        # _form.program = fields.Integer(choices=_choices)
        # _form.sec = fields.Button("Seç")
        # self.form_out(_form)

    def kayit_tarihi_kontrol(self):
        self.current.task_data["kayit_tarih_kontrol"] = True

        # self.current.task_data["birim"] = self.current.input['form']['SilmeForm']
        # for secilen_birim in self.current.task_data["birim"]:
        #     if secilen_birim['secim'] == True:
        #         birim = secilen_birim['birim_ad']
        #
        # bitis_tarihi = get_akademik_takvim(birim)

        # if date.today() > ders_kayit_son_tarih:
        #     self.current.task_data["kayit_tarih_kontrol"] = True
        #
        # else:
        #     self.current.task_data["kayit_tarih_kontrol"] = False

        # en_son_bitis_tarihi=[]
        # son_kayit_tarihleri = AkademikTakvim.objects.filter(birim=birim)
        # for son_tarih in son_kayit_tarihleri:
        #     en_son_bitis_tarihi.append(son_tarih.Takvim[9].bitis)
        # ders_kayit_son_tarih = max(en_son_bitis_tarihi)

    def silinecek_ogrenci_kontrol(self):

        self.current.task.data["secim"] = True

        # self.current.task_data["birim"] = self.current.input['form']['SilmeForm']
        # for secilen_birim in self.current.task_data["birim"]:
        #     if secilen_birim['secim'] == True:
        #         birim = secilen_birim['birim_ad']
        #         form_sira = secilen_birim['form_sira']
        #
        # if form_sira == 1:
        #
        #     if len(OgrenciProgram.objects.filter(durum=1, bagli_oldugu_ana_birim_turu=birim)) > 0:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = True
        #     else:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = False
        #
        # if form_sira == 2:
        #
        #     if len(OgrenciProgram.objects.filter(durum=1, bagli_oldugu_ana_birim=birim)) > 0:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = True
        #     else:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = False
        #
        # if form_sira == 3:
        #
        #     if len(OgrenciProgram.objects.filter(durum=1, bolum=birim)) > 0:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = True
        #     else:
        #         self.current.task_data["silinecek_ogrenci_kontrol"] = False

    def personel_onay(self):

        # self.current.output['msgbox'] = {
        #     'type': 'info', "title": 'Onay',
        #     "msg": 'Seçilen Birimlerdeki Kaydı Gerçekleşmeyen Öğrencileri Silmek İstiyor musunuz?'
        # }

        _form = JsonForm(current=self.current, title="Uyarı Mesajı")
        _form.help_text = """Seçilen birimdeki öğrencileri silmek üzeresiniz. Bu işlemi
        onaylamak için Tamamla butonuna basınız. İptal edip geri dönmek istiyorsanız
        İptal butonuna basınız."""
        _form.geri_don = fields.Button("Tamamla", flow="secilen_on_kayit_sil")
        self.form_out(_form)

    def secilen_on_kayit_sil(self):

        secilen = self.current.task_data["secilen"][0]
        birim = secilen['birim_ad']

        silinecek_ogrenciler = OgrenciProgram.objects.filter(durum=1, bagli_oldugu_ana_birim_turu=birim)

        for silinecek_ogrenci in silinecek_ogrenciler:
            silinecek_ogrenci.durum = 0
            silinecek_ogrenci.save()

    def personel_bilgilendir(self):

        _form = JsonForm(current=self.current, title="Uyarı Mesajı")
        _form.help_text = """Seçilen birimdeki öğrenciler başarıyla silindi."""
        _form.geri_don = fields.Button("Tamamla", flow="secilen_on_kayit_sil")
        self.form_out(_form)

    def personel_silme_uyari(self):

        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Uyarı Mesajı',
            "msg": 'Silinecek .'
        }

    def personel_kayit_uyari(self):

        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Uyarı Mesajı',
            "msg": """Kayıt işlemi devam etmektedir! Silme işlemini gerçekleştirebilmek
                      için kayıt işleminin bitmesini bekleyiniz."""
        }
