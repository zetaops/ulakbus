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


class ProgramDersForm(JsonForm):
    """
    Kopyalanan dersleri tabloda gösterirken kullanılan form.

    """

    class Meta:
        inline_edit = ['secim']

    class SilmeForm(ListNode):
        secim = fields.Boolean(type="checkbox")
        birim_ad = fields.String("Ad", hidden=True)
        tanim = fields.String("Tanım", index=True)
        durum = fields.Integer("Durum", hidden=True)
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

        _form.SilmeForm(secim=False, birim_ad="Üniversitedeki Ön Kayıtta Bulunan Bütün Ögrencileri Sil")

        for type in birim_type:
            if not type in ['İdari', 'Rektörlük']:
                _form.SilmeForm(secim=False, tanim=type, birim_ad=type, durum=0)
                _form.SilmeForm(secim=False, tanim=type + " Birimine Ait Ön Kayıttaki Bütün Ögrencileri Sil",
                                birim_ad=type, durum=1)
        _form.duzenle = fields.Button("İlerle")
        self.form_out(_form)

    def on_kayit_silme_tercih_form_2(self):

        self.current.task_data["gelen_form"] = self.current.input['form']['SilmeForm']
        for birim in self.current.task_data["gelen_form"]:
            if birim['secim']:
                unit_type = birim['birim_ad']
                # self.current.task_data["secilen_birim"] = unit_type
                # secilen_birim = Unit.objects.filter(unit_type =unit_type)

        _form = JsonForm(current=self.current, title="Silinecek Birimi Seçiniz")
        _choices = prepare_choices_for_model(Unit, is_active=True, unit_type=unit_type)

        _form.program = fields.Integer(choices=_choices)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

        # _form = ProgramDersForm(current=self.current,
        #                         title="Kaydı Gerçekleşmeyen Ön Kayıt Öğrencilerini Silmek İstediğiniz Birimi Seçiniz")
        #
        # for birim in secilen_birim:
        #     if birim.is_active:
        #         _form.SilmeForm(secim=False, birim_ad=birim.name)
        # _form.duzenle = fields.Button("Onayla")
        # self.form_out(_form)

    def kayit_tarihi_kontrol(self):

        self.current.task_data["birim"] = self.current.input['form']['SilmeForm']
        for secilen_birim in self.current.task_data["birim"]:
            if secilen_birim['secim'] == True:
                birim = secilen_birim['birim_ad']

        en_son_bitis_tarihi=[]
        son_kayit_tarihleri = AkademikTakvim.objects.filter(birim=birim)
        for son_tarih in son_kayit_tarihleri:
            en_son_bitis_tarihi.append(son_tarih.Takvim[9].bitis)
        ders_kayit_son_tarih = max(en_son_bitis_tarihi)


        if date.today() > ders_kayit_son_tarih:
            self.current.task_data["kayit_tarih_kontrol"] = True
        else:
            self.current.task_data["kayit_tarih_kontrol"] = False

    def silinecek_ogrenci_kontrol(self):

        if len(OgrenciProgram.objects.filter(durum=1)) > 0:
            self.current.task_data["silinecek_ogrenci_kontrol"] = True
        else:
            self.current.task_data["silinecek_ogrenci_kontrol"] = False

    def secilen_on_kayit_sil(self):

        pass

    def personel_bilgilendir(self):

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Onay Mesajı',
            "msg": 'Silme işleminiz başarıyla gerçekleştirildi.'
        }

    def personel_silme_uyari(self):

        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Uyarı Mesajı',
            "msg": 'Silinecek ön kayıt kaydı bulunmamaktadır.'
        }

    def personel_kayit_uyari(self):

        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Uyarı Mesajı',
            "msg": """Kayıt işlemi devam etmektedir! Silme işlemini gerçekleştirebilmek
                      için kayıt işleminin bitmesini bekleyiniz."""
        }
