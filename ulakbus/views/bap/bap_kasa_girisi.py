# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import OrderedDict
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext_lazy as __
import datetime
from pyoko.fields import DATE_TIME_FORMAT
from ulakbus.models.bap.bap import BAPGenel
from ulakbus.models.bap.bap import BapKasaHareketi
from ulakbus.settings import DATE_DEFAULT_FORMAT


class KasaGirisiForm(JsonForm):
    para_miktari = fields.Float(__(u"Para Miktarı"))
    giris_tarihi = fields.Date(__(u"Giriş Tarihi"),
                               default=datetime.date.today().strftime(DATE_TIME_FORMAT))
    kaydet = fields.Button(__(u"Kaydet"))


class KayitOnayForm(JsonForm):
    onayla = fields.Button(__(u"Onayla"), cmd='onayla')
    iptal = fields.Button(__(u"İptal"))


class KasaIslemGecmisiForm(JsonForm):
    """
    Kasa Geçmişinin Gösterildiği form

    """

    class Meta:
        title = __(u"Kasa İşlem Geçmişi")

    ekle = fields.Button(__(u"Ekle"), cmd='ekle')
    ana_menu_don = fields.Button(__(u"Ana Menüye Dön"))


class KasaGirisi(CrudView):
    class Meta:
        model = "BAPGenel"

    def kasa_giris_yap(self):
        """
        Para miktarı ve tarihin girildiği form

        """
        _form = KasaGirisiForm(current=self.current,
                               title=__(u"Lütfen Kasa Girişi Yapınız"))
        self.form_out(_form)

    def onay_form(self):
        """
        Para Girişinin Onaylanma veya İptal Formu

        """
        bilgi_ver = OrderedDict([
            ('Miktar', str(self.current.input['form']['para_miktari'])),
            ('Giriş Tarihi', self.current.input['form']['giris_tarihi']),
        ])
        self.output['object'] = bilgi_ver
        self.form_out(KayitOnayForm(title=__('Kasa Girişi Onay Form')))

    def kaydet(self):
        """
        Formdan gelen para miktarını toplam_kasa ya ekleyerek gunceller
        ListNode olan tarih ve miktar da eklenir

        """

        miktar = self.current.task_data['KasaGirisiForm']['para_miktari']
        tarih = self.current.task_data['KasaGirisiForm']['giris_tarihi']
        kasa_hareketi = BapKasaHareketi(miktar=miktar, tarih=tarih,
                                        sebep=1)
        genel = BAPGenel.get()
        genel.toplam_kasa += miktar
        genel.blocking_save()
        kasa_hareketi.blocking_save()

    def kayit_giris_bilgilendirme(self):
        """
        Kayıt bilgi form
        """
        form = JsonForm(title="Kasa Giriş Kaydı")
        form.help_text = "Kasa giriş kaydınız başarılı bir şekilde gerçekleştirildi"
        form.tamam = fields.Button(__(u'Tamam'))
        self.form_out(form)

    def yonlendir(self):
        """
        Anasayfaya Yonlendirme İşlemi
        """
        self.current.output['cmd'] = 'reload'

    def kasa_gecmisi_listele(self):
        """
        Kasa Girişinin Başarılı bir şekilde gerçekleştiğini gösterme
        """

        self.current.output["meta"]["allow_actions"] = False  # yapılacak bir işlem yok
        # bap_genel = BAPGenel.get()
        self.output['objects'] = [[__(u'Miktar'), __(u'Tarih'), __(u"Sebep")]]
        for islem in BapKasaHareketi.objects.filter().order_by('-tarih'):
            miktar = islem.miktar
            sebep = islem.sebep
            tarih = islem.tarih.strftime(DATE_DEFAULT_FORMAT) if islem.tarih else ''
            list_item = {
                "fields": [str(miktar), tarih, str(sebep)],
                "actions": '',
            }
            self.output['objects'].append(list_item)
        self.form_out(KasaIslemGecmisiForm())
