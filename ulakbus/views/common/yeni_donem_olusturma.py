# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
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

    @staticmethod
    def en_son_kaydedilen_bahar_donemi():
        """
        Returns:
             Veritabanında kayıtlı olan en son bahar dönemini

        """

        donemler = Donem.objects.filter()
        for donem in donemler:
            if all(donem.bitis_tarihi.year >= donm.bitis_tarihi.year for donm in donemler):
                return donem

    @staticmethod
    def en_son_kaydedilen_guz_donemi():
        """
        Returns:
             Veritabanında kayıtlı olan en son güz dönemini
        """
        en_son_kaydedilen_bahar_donemi = YeniDonemOlusturma.en_son_kaydedilen_bahar_donemi()
        en_son_kaydedilen_guz_donemi_yili = en_son_kaydedilen_bahar_donemi.bitis_tarihi.year - 1
        donemler = Donem.objects.filter()
        lst_donem = [donem for donem in donemler if
                     donem.baslangic_tarihi.year == en_son_kaydedilen_guz_donemi_yili and donem.ad == 'Güz Dönemi']
        if len(lst_donem) == 1:
            return lst_donem[0]

        else:
            raise Exception(
                '{0} yılına ait birden fazla güz dönemi kayıtlıdır.'.format(en_son_kaydedilen_guz_donemi_yili))

    @staticmethod
    def guncel_donem_bul():
        """
        Returns:
             Veritabanında kayıtlı olan güncel dönemi
        """
        donemler = Donem.objects.filter()
        lst_guncel_donem = [donem for donem in donemler if donem.guncel]
        if len(lst_guncel_donem) == 1:
            return lst_guncel_donem[0]

        else:
            raise Exception('Sisteminizde birden fazla güncel dönem kayıtlıdır.')

    def donem_formu_olustur(self):
        """
        Güz ve Bahar Dönemi Formu oluşturulur.

        """

        _form = DonemForm(current=self.current, title='Güz ve Bahar Dönemi')
        try:
            son_bahar_donemi = YeniDonemOlusturma.en_son_kaydedilen_bahar_donemi()
            son_guz_donemi = YeniDonemOlusturma.en_son_kaydedilen_guz_donemi()
            guncel_donem = YeniDonemOlusturma.guncel_donem_bul()
            _form.help_text = "En son kaydedilen donemler {0} ve {1},Güncel Dönem {2}," \
                              "{3} Güz Dönem ve {4} Bahar Dönemi Kaydedebilirsiniz".format(
                son_bahar_donemi, son_guz_donemi, guncel_donem,
                son_bahar_donemi.bitis_tarihi.year,
                son_bahar_donemi.bitis_tarihi.year + 1)

        except AttributeError:
            pass
        self.form_out(_form)

    def donem_formu_kaydet(self):
        """
        Doldurulan dönem formu bilgilerine göre güz ve bahar dönemi oluşturulup kaydedilir.

        """

        del self.current.input['form']['kaydet']
        bahar_donemi = Donem()
        bahar_donemi.ad = 'Bahar Dönemi'
        bahar_donemi.baslangic_tarihi = self.current.input['form']['bahar_baslangic_tarihi']
        bahar_donemi.bitis_tarihi = self.current.input['form']['bahar_bitis_tarihi']
        bahar_donemi.save()

        guz_donemi = Donem()
        guz_donemi.ad = 'Güz Dönemi'
        guz_donemi.baslangic_tarihi = self.current.input['form']['guz_baslangic_tarihi']
        guz_donemi.bitis_tarihi = self.current.input['form']['guz_bitis_tarihi']
        guz_donemi.save()

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı basılır.

        """

        self.current.output['msgbox'] = {
            'type': 'error', "title": 'Güz ve Bahar Dönemi',
            "msg": 'Güz ve Bahar Dönemi başarıyla oluşturulmuştur.'
        }
