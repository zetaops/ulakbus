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
from zengine.lib.translation import gettext as _, gettext_lazy, format_date


class DonemForm(forms.JsonForm):
    """
    Yeni Dönem Oluşturma iş akışı için kullanılacak formdur.

    """

    guz_baslangic_tarihi = fields.Date(gettext_lazy(u"Başlangıç Tarihi"), format="%d.%m.%Y", required=True)
    guz_bitis_tarihi = fields.Date(gettext_lazy(u"Bitiş Tarihi"), index=True, format="%d.%m.%Y", required=True)
    bahar_baslangic_tarihi = fields.Date(gettext_lazy(u"Başlangıç Tarihi"), index=True, format="%d.%m.%Y",
                                         required=True)
    bahar_bitis_tarihi = fields.Date(gettext_lazy(u"Bitiş Tarihi"), index=True, format="%d.%m.%Y", required=True)

    class Meta:
        grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Güz Dönemi"),
                        "items": ['guz_baslangic_tarihi', 'guz_bitis_tarihi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Bahar Dönemi"),
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

    kaydet = fields.Button(gettext_lazy(u"Kaydet"))


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

        _form = DonemForm(current=self.current, title=_(u'Güz ve Bahar Dönemi'))

        son_donem = Donem.son_donem()

        _form.help_text = _(u"""Kayıtlardaki en son donem {donem}
        Başlangıç Tarihi: {baslangic},
        Bitiş Tarihi: {bitis}
        """).format(donem=son_donem.ad,
                    baslangic=format_date(son_donem.baslangic_tarihi),
                    bitis=format_date(son_donem.bitis_tarihi))

        self.form_out(_form)

    def donem_formu_kaydet(self):
        """
        Doldurulan dönem formu bilgilerine göre güz ve bahar dönemi oluşturulup kaydedilir.

        """

        def yeni_donem(ad, baslangic, bitis):
            d = Donem(
                ad='%s - %s' % (ad, baslangic.split('.')[2]),
                baslangic_tarihi=baslangic,
                bitis_tarihi=bitis
            )
            d.save()

        fdata = self.current.input['form']

        yeni_donem(_(u'Bahar'), fdata['bahar_baslangic_tarihi'], fdata['bahar_bitis_tarihi'])
        yeni_donem(_(u'Güz'), fdata['guz_baslangic_tarihi'], fdata['guz_bitis_tarihi'])

    def bilgi_ver(self):
        """
        İşlemin başarılı olduğuna dair bilgilendirme mesajı basılır.

        """

        self.current.output['msgbox'] = {
            'type': 'bilgilendirme', "title": _(u'Güz ve Bahar Dönemi'),
            "msg": _(u'Güz ve Bahar Dönemi başarıyla oluşturulmuştur.')
        }
