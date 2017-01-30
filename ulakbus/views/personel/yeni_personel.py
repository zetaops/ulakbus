# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from pyoko.exceptions import ObjectDoesNotExist
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy
from ulakbus.models.personel import Personel
import random
from datetime import datetime

"""
``button`` nesnelerinin stillendirilmesi için bu nesnelere ``style`` anahtarı ile css class'ları
gönderilebilir. Bu class'lar şunlar olabilir:
​
    - btn-default
    - btn-primary
    - btn-success
    - btn-info
    - btn warning
"""


# Views
class YeniPersonelEkle(CrudView):
    class Meta:
        model = 'Personel'

    def yeni_personel_form(self):
        """

        Yeni Personel eklenirken Tc Kimlik Numarası ekranı getirmek için kullanılan fonksiyon

        """
        _form = YeniPersonelTcknForm(current=self.current)
        self.form_out(_form)

    def mernis_kimlik_bilgileri_getir(self):
        tckn = self.current.input['form']['tckn']

        # Personelin daha önce bulunup bulunmadığını kontrol et
        try:
            Personel.objects.get(tckn=tckn)
            self.current.task_data['mernis_tamam'] = False
            self.current.task_data['hata_msg'] = _(u"Personel Daha Önce Kaydedilmiş")
        except ObjectDoesNotExist:
            # Kimlik bilgileri mernis servisi üzerinden çekilecek
            service_name = 'kisi-sorgula-tc-kimlik-no'
            mernis_bilgileri = TcknService(service_name=service_name,
                                           payload={"tckn": str(tckn)})
            response = mernis_bilgileri.zato_request()
            self.current.task_data['mernis_tamam'] = True
            self.current.task_data['kimlik_bilgileri'] = response

            # Cüzdan bilgileri mernis servisi üzerinden çekilecek
            service_name = 'cuzdan-sorgula-tc-kimlik-no'
            mernis_bilgileri = TcknService(service_name=service_name,
                                           payload={"tckn": str(tckn)})
            response = mernis_bilgileri.zato_request()
            self.current.task_data['cuzdan_tamam'] = True
            self.current.task_data['cuzdan_bilgileri'] = response
            self.current.task_data['tckn'] = tckn

            self.current.set_message(title=_(u'%s TC no için Mernis servisi başlatıldı') % tckn,
                                     msg='', typ=1, url="/wftoken/%s" % self.current.token)

    def mernis_adres_bilgileri_getir(self, tckn=None):
        if not tckn:
            tckn = self.current.task_data['tckn']
        # Adres bilgileri mernis servisi üzerinden çekilecek
        service_name = 'adres-sorgula'
        mernis_bilgileri = TcknService(service_name=service_name,
                                       payload={"tckn": str(tckn)})
        response = mernis_bilgileri.zato_request()

        self.current.task_data['adres_tamam'] = True
        self.current.task_data['adres_bilgileri'] = response

        return response

    def yeni_ekle_kontrol(self):
        _form = IletisimveEngelliDurumBilgileriForm(current=self.current)
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Personel Kayıt Uyarısı'),
            "msg": _(u"""
                      Lütfen Personel bilgilerinin doğruluğunu kontrol ediniz.
                      Kayıt işlemi geri döndürülemez.
                      """)
        }
        #
        # _form.ikamet_adresi = self.current.task_data['adres_bilgileri']['ikamet_adresi']
        # _form.ikamet_il = self.current.task_data['adres_bilgileri']['ikamet_il']
        # _form.ikamet_ilce = self.current.task_data['adres_bilgileri']['ikamet_ilce']

        _form.kaydet = fields.Button(_(u"Kaydet (Bu işlem geri alınamaz!)"), cmd="kaydet",
                                     btn='success')
        _form.iptal = fields.Button(_(u"İptal"), cmd="iptal", flow="iptal", form_validation=False)

        # kimlik_bilgileri = _(u"""**Adı**: {ad}
        #                       **Soyad**: {soyad}
        #                       **Doğum Tarihi**: {dogum_tarihi}
        #                       """).format(**self.current.task_data['kimlik_bilgileri'])

        # adres_bilgileri = _(u"""**İl**: {ikamet_il}
        #                      **İlçe**: {ikamet_ilce}
        #                      **Adres**: {ikamet_adresi}
        #                      """).format(**self.current.task_data['adres_bilgileri'])
        #
        # output = [{_(u'Kişi Bilgileri'): kimlik_bilgileri, _(u'Adres Bilgileri'): adres_bilgileri}]
        #
        # self.current.output['object'] = {
        #     "type": "table-multiRow",
        #     "title": _(u"Kişi Bilgileri"),
        #     "fields": output,
        #     "actions": False
        # }

        self.current.task_data['tckn'] = random.randrange(12345678909)
        self.form_out(_form)

    def kaydet(self):
        yeni_personel = Personel()
        yeni_personel.tckn = self.current.task_data['tckn']


        # Task data içinde gelen bilgiler birleştirilecek
        personel_data = {}
        # personel_data.update(self.current.task_data['kimlik_bilgileri'])
        # personel_data.update(self.current.task_data['cuzdan_bilgileri'])
        # personel_data.update(self.current.task_data['adres_bilgileri'])

        for key in personel_data:
            setattr(yeni_personel, key, personel_data[key])

        yeni_personel.ad = 'Yeni' + str(random.randrange(1000))
        yeni_personel.soyad = 'Personel' + str(random.randrange(1000))
        yeni_personel.blocking_save()

        self.current.task_data['personel_id'] = yeni_personel.key

    def kadro_derece_bilgi_ekrani(self):

        _form = KadroDereceForm(current=self.current)
        _form.kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet")
        self.form_out(_form)

    def kadro_derece_kaydet(self):
        p = Personel.objects.get(self.current.task_data['personel_id'])
        for k,v in self.input['form'].items():
            if hasattr(p,k):
                try:
                    setattr(p,k,datetime.strptime(v, '%d.%m.%Y').date())
                except:
                    setattr(p, k, v)

        p.blocking_save()

        _form = JsonForm(current=self.current)
        _form.title = _(u"Devam Etmek İstediğiniz İşlemi Seçiniz")
        _form.help_text = _(u"""%s %s adlı personel başarı ile kaydedildi. Personele
                                atama yapabilir veya daha sonra atama yapmak için "İşlemi Bitir"
                                butonuna tıklayabilirsiniz.""" %(p.ad,p.soyad))

        # todo: bu buton ilgili personel secili olarak yeni bir wf baslatacak
        _form.atama = fields.Button(_(u"Atama Yap"), style="btn-success", cmd="atama_yap")

        _form.iptal = fields.Button(_(u"İşlemi Bitir"), cmd="bitir")
        self.form_out(_form)

    def hata_goster(self):
        if self.current.task_data['hata_msg']:
            msg = self.current.task_data['hata_msg']
        else:
            msg = _(u"Bilinmeyen bir hata oluştu.")
        self.current.output['msgbox'] = {
            'type': 'error', "title": _(u'İşlem Başarısız'),
            "msg": msg
        }

        _form = JsonForm(current=self.current)
        _form.geri = fields.Button(_(u"Yeni bir Tc Kimlik Numarası ile dene"), style="btn-success",
                                   cmd="tekrar")
        _form.iptal = fields.Button(_(u"İptal"), cmd="iptal")
        self.form_out(_form)


# Formlar
class YeniPersonelTcknForm(JsonForm):
    class Meta:
        title = gettext_lazy(u'Yeni Personel Ekle')
        help_text = gettext_lazy(u"Kimlik Numarası ile MERNIS ve HITAP bilgileri getir.")

    tckn = fields.String(gettext_lazy(u"TC No"))
    cmd = fields.String(gettext_lazy(u"Bilgileri Getir"), type="button")


class IletisimveEngelliDurumBilgileriForm(JsonForm):
    class Meta:
        title = gettext_lazy(u'Bilgi Kontrol Ekranı')
        # help_text = gettext_lazy(u"Yeni Personelin Iletisim Bilgilerini Duzenle.")
        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Adres Bilgileri"),
                        "items": ['ikamet_adresi', 'ikamet_il', 'ikamet_ilce',
                                  'adres_2', 'adres_2_posta_kodu'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"İletişim Bilgileri"),
                        "items": ['oda_tel_no', 'cep_telefonu', 'e_posta', 'e_posta_2',
                                  'e_posta_3', 'web_sitesi', 'notlar'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "12",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Engel Bilgileri"),
                        "items": ['engelli_durumu', 'engel_grubu', 'engel_derecesi', 'engel_orani']
                    }
                ]
            },
        ]

    ikamet_adresi = fields.Text(gettext_lazy(u"İkamet Adresi"))
    ikamet_il = fields.String(gettext_lazy(u"İkamet Il"))
    ikamet_ilce = fields.String(gettext_lazy(u"İkamet Ilce"))
    adres_2 = fields.String(gettext_lazy(u"Adres 2"))
    adres_2_posta_kodu = fields.String(gettext_lazy(u"Adres 2 Posta Kodu"))
    oda_tel_no = fields.String(gettext_lazy(u"Oda Telefon Numarası"))
    cep_telefonu = fields.String(gettext_lazy(u"Cep Telefonu"))
    e_posta = fields.String(gettext_lazy(u"Kurum E-Posta(Yeni Personel için boş bırakınız)"), required=False)
    e_posta_2 = fields.String(gettext_lazy(u"E-Posta 2"), required=False)
    e_posta_3 = fields.String(gettext_lazy(u"E-Posta 3"), required=False)
    web_sitesi = fields.String(gettext_lazy(u"Web Sitesi"), required=False)
    notlar = fields.Text(gettext_lazy(u"Not"), required=False)
    engelli_durumu = fields.String(gettext_lazy(u"Engellilik"), required=False)
    engel_grubu = fields.String(gettext_lazy(u"Engel Grubu"), required=False)
    engel_derecesi = fields.String(gettext_lazy(u"Engel Derecesi"), required=False)
    engel_orani = fields.Integer(gettext_lazy(u"Engellilik Orani"), required=False)

class KadroDereceForm(JsonForm):
    class Meta:
        title = gettext_lazy(u'Personel Kadro Derece Bilgileri')
        grouping = [
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"Görev Aylığı Bilgileri"),
                        "items": ['gorev_ayligi_derece', 'gorev_ayligi_kademe',
                                  'gorev_ayligi_ekgosterge', 'ga_sonraki_terfi_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"K. Hak Aylığı Bilgileri"),
                        "items": ['kazanilmis_hak_derece', 'kazanilmis_hak_kademe',
                                  'kazanilmis_hak_ekgosterge', 'kh_sonraki_terfi_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": gettext_lazy(u"E. Müktesebi Bilgileri"),
                        "items": ['emekli_muktesebat_derece', 'emekli_muktesebat_kademe',
                                  'emekli_muktesebat_ekgosterge', 'em_sonraki_terfi_tarihi'],
                    },
                ]
            }
        ]

    kazanilmis_hak_derece = fields.Integer(_(u"Derece"))
    kazanilmis_hak_kademe = fields.Integer(_(u"Kademe"))
    kazanilmis_hak_ekgosterge = fields.Integer(_(u"Ek Gösterge"), required=False)
    gorev_ayligi_derece = fields.Integer(_(u"Derece"))
    gorev_ayligi_kademe = fields.Integer(_(u"Kademe"))
    gorev_ayligi_ekgosterge = fields.Integer(_(u"Ek Gösterge"), required=False)
    emekli_muktesebat_derece = fields.Integer(_(u"Derece"))
    emekli_muktesebat_kademe = fields.Integer(_(u"Kademe"))
    emekli_muktesebat_ekgosterge = fields.Integer(_(u"Ek Gösterge"), required=False)
    kh_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")
    ga_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")
    em_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")
