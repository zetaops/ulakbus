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

    guz_baslangic_tarihi = fields.Date("Başlangıç Tarihi", format="%d.%m.%Y")
    guz_bitis_tarihi = fields.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y", required=True)
    bahar_baslangic_tarihi = fields.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y", required=True)
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
        son_bahar_donemi = Donem.en_son_bahar_donemi()
        son_guz_donemi = Donem.en_son_guz_donemi()
        guncel_donem = Donem.guncel_donem()
        _form.help_text = "En son kaydedilen donemler {0} ve {1},Güncel Dönem {2}," \
                          "{3} Güz Dönem ve {4} Bahar Dönemi Kaydedebilirsiniz".format(
            son_bahar_donemi, son_guz_donemi, guncel_donem,
            son_bahar_donemi.bitis_tarihi.year,
            son_bahar_donemi.bitis_tarihi.year + 1)
        self.form_out(_form)

    def donem_formu_kaydet(self):
        """
        Doldurulan dönem formu bilgilerine göre güz ve bahar dönemi oluşturulup kaydedilir.

        """

        del self.current.input['form']['kaydet']
        bahar_donemi = Donem()
        bahar_donemi.ad = 'Bahar - %s ' % datetime.strptime(self.current.input['form']['bahar_baslangic_tarihi'], "%d.%m.%Y")
        bahar_donemi.baslangic_tarihi = self.current.input['form']['bahar_baslangic_tarihi']
        bahar_donemi.bitis_tarihi = self.current.input['form']['bahar_bitis_tarihi']
        bahar_donemi.save()

        guz_donemi = Donem()
        guz_donemi.ad = 'Güz - %s' % datetime.strptime(self.current.input['form']['guz_baslangic_tarihi'], "%d.%m.%Y")
        guz_donemi.baslangic_tarihi = self.current.input['form']['guz_baslangic_tarihi']
        guz_donemi.bitis_tarihi = self.current.input['form']['guz_bitis_tarihi']
        guz_donemi.save()

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı basılır.

        """

        self.current.output['msgbox'] = {
            'type': 'bilgilendirme', "title": 'Güz ve Bahar Dönemi',
            "msg": 'Güz ve Bahar Dönemi başarıyla oluşturulmuştur.'
        }
