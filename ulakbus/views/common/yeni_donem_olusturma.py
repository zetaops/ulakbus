# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import datetime

from ulakbus.models import Donem
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView


class DonemForm(forms.JsonForm):
    """
    Yeni Dönem Oluşturma iş akışı için kullanılacak formdur.

    """

    guz_baslangic_tarihi = fields.Date("Başlangıç Tarihi", format="%d.%m.%Y", required=True)
    guz_bitis_tarihi = fields.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y", required=True)
    bahar_baslangic_tarihi = fields.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y",
                                         required=True)
    bahar_bitis_tarihi = fields.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y", required=True)

    class Meta:
        grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Güz Dönemi",
                        "items": ['guz_baslangic_tarihi', 'guz_bitis_tarihi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": "Bahar Dönemi",
                        "items": ['bahar_baslangic_tarihi', 'bahar_bitis_tarihi'],
                        "collapse": True,

                    }
                ]
            },
            {
                "layout": "7",
                "groups": [
                    {
                        "items": ['kaydet']
                    }
                ]
            }

        ]

    kaydet = fields.Button("Kaydet")


class YeniDonemOlusturma(CrudView):
    """
    Yeni Dönem Oluşturma iş akışı üç adımdan oluşmaktadır.

    Dönem Formu Oluştur:
    Güz ve Bahar Dönemi Formu oluşturulur.

    Dönem Formu Kaydet:
    Doldurulan dönem formu bilgilerine göre güz ve bahar dönemi oluşturulup kaydedilir.

    Bilgi Ver:
    İşlemin başarılı olduğuna dair bilgilendirme mesajı basılır.

    """

    class Meta:
        model = "Donem"

    def donem_formu_olustur(self):
        """
        Güz ve Bahar Dönemi Formu oluşturulur.

        """

        _form = DonemForm(current=self.current, title='Güz ve Bahar Dönemi')

        son_donem = Donem.son_donem()

        _form.help_text = """Kayıtlardaki en son donem {}
        Başlangıç Tarihi: {:%d.%m.%Y},
        Bitiş Tarihi: {:%d.%m.%Y}
        """.format(son_donem.ad,
                   son_donem.baslangic_tarihi,
                   son_donem.bitis_tarihi)

        self.form_out(_form)

    def donem_formu_kaydet(self):
        """
        Doldurulan dönem formu bilgilerine göre güz ve bahar dönemi oluşturulup kaydedilir.

        """

        def yeni_donem(ad, baslangic, bitis):
            d = Donem(
                ad='%s - %s' % (ad, baslangic.split('.')[2]),
                baslangic=baslangic,
                bitis=bitis
            )
            d.save()

        fdata = self.current.input['form']

        yeni_donem('Bahar', fdata['bahar_baslangic_tarihi'], fdata['bahar_bitis_tarihi'])
        yeni_donem('Güz', fdata['guz_baslangic_tarihi'], fdata['guz_bitis_tarihi'])

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı basılır.

        """

        self.current.output['msgbox'] = {
            'type': 'bilgilendirme', "title": 'Güz ve Bahar Dönemi',
            "msg": 'Güz ve Bahar Dönemi başarıyla oluşturulmuştur.'
        }
