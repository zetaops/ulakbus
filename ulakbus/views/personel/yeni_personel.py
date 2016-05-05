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
from ulakbus.models.personel import Personel

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
            self.current.task_data['hata_msg'] = "Personel Daha Önce Kaydedilmiş"
        except ObjectDoesNotExist:
            from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir, \
                MernisCuzdanBilgileriGetir

            # Kimlik bilgileri mernis servisi üzerinden çekilecek
            mernis_bilgileri = MernisKimlikBilgileriGetir(tckn=str(tckn))
            response = mernis_bilgileri.zato_request()
            self.current.task_data['mernis_tamam'] = True
            self.current.task_data['kimlik_bilgileri'] = response
            # Cüzdan bilgileri mernis servisi üzerinden çekilecek
            mernis_bilgileri = MernisCuzdanBilgileriGetir(tckn=str(tckn))
            response = mernis_bilgileri.zato_request()
            self.current.task_data['cuzdan_tamam'] = True
            self.current.task_data['cuzdan_bilgileri'] = response
            self.current.task_data['tckn'] = tckn

            self.current.set_message(title='%s TC no için Mernis servisi başlatıldı' % tckn,
                                     msg='', typ=1, url="/wftoken/%s" % self.current.token)

    def mernis_adres_bilgileri_getir(self, tckn=None):
        if not tckn:
            tckn = self.current.input['form']['tckn']
        # Adres bilgileri mernis servisi üzerinden çekilecek
        from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
        mernis_bilgileri = KPSAdresBilgileriGetir(tckn=str(tckn))
        response = mernis_bilgileri.zato_request()

        self.current.task_data['adres_tamam'] = True
        self.current.task_data['adres_bilgileri'] = response

        return response

    def yeni_ekle_kontrol(self):
        _form = IletisimveEngelliDurumBilgileriForm(current=self.current)
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Personel Kayıt Uyarısı',
            "msg": """
                   Lütfen Personel bilgilerinin doğruluğunu kontrol ediniz.
                   Kayıt işlemi geri döndürülemez.
                   """
        }

        _form.ikamet_adresi = self.current.task_data['adres_bilgileri']['ikamet_adresi']
        _form.ikamet_il = self.current.task_data['adres_bilgileri']['ikamet_il']
        _form.ikamet_ilce = self.current.task_data['adres_bilgileri']['ikamet_ilce']

        _form.kaydet = fields.Button("Kaydet (Bu işlem geri alınamaz!)", cmd="kaydet",
                                     btn='success')
        _form.iptal = fields.Button("İptal", cmd="iptal", flow="iptal", form_validation=False)

        kimlik_bilgileri = """**Adı**: {ad}
                           **Soyad**: {soyad}
                           **Doğum Tarihi**: {dogum_tarihi}
                           """.format(**self.current.task_data['kimlik_bilgileri'])

        adres_bilgileri = """**İl**: {ikamet_il}
                          **İlçe**: {ikamet_ilce}
                          **Adres**: {ikamet_adresi}
                          """.format(**self.current.task_data['adres_bilgileri'])

        output = [{'Kişi Bilgileri': kimlik_bilgileri, 'Adres Bilgileri': adres_bilgileri}]

        self.current.output['object'] = {
            "type": "table-multiRow",
            "title": "Kişi Bilgileri",
            "fields": output,
            "actions": False
        }
        self.form_out(_form)

    def kaydet(self):
        yeni_personel = Personel()
        yeni_personel.tckn = self.current.task_data['tckn']

        # Task data içinde gelen bilgiler birleştirilecek
        personel_data = {}
        personel_data.update(self.current.task_data['kimlik_bilgileri'])
        personel_data.update(self.current.task_data['cuzdan_bilgileri'])
        personel_data.update(self.current.task_data['adres_bilgileri'])

        for key in personel_data:
            setattr(yeni_personel, key, personel_data[key])

        yeni_personel.save()

        self.current.output['msgbox'] = {
            'type': 'success',
            "title": '%s %s Başarı İle Kaydedildi' % (yeni_personel.ad, yeni_personel.soyad),
            "msg": """
                   Personel Başarı ile Kaydedildi, Personele atama yapabilir veya daha sonra
                   atama yapmak için "İşlemi Bitir" Butonuna tıklayabilirsiniz
                   """
        }

        _form = JsonForm(current=self.current)

        # todo: bu buton ilgili personel secili olarak yeni bir wf baslatacak
        _form.geri = fields.Button("Atama Yap", style="btn-success", cmd="atama_yap")

        _form.iptal = fields.Button("İşlemi Bitir", cmd="bitir")
        self.form_out(_form)

        self.current.task_data['personel_id'] = yeni_personel.key

    def hata_goster(self):
        if self.current.task_data['hata_msg']:
            msg = self.current.task_data['hata_msg']
        else:
            msg = "Bilinmeyen bir hata oluştu :( sebebini biliyorsanız bizede söyleyinde düzeltelim"
        self.current.output['msgbox'] = {
            'type': 'error', "title": 'İşlem Başarısız',
            "msg": msg
        }

        _form = JsonForm(current=self.current)
        _form.geri = fields.Button("Yeni bir Tc Kimlik Numarası ile dene", style="btn-success",
                                   cmd="tekrar")
        _form.iptal = fields.Button("İptal", cmd="iptal")
        self.form_out(_form)


# Formlar
class YeniPersonelTcknForm(JsonForm):
    class Meta:
        title = 'Yeni Personel Ekle'
        help_text = "Kimlik Numarası ile MERNIS ve HITAP bilgileri getir."

    tckn = fields.String("TC No")
    cmd = fields.String("Bilgileri Getir", type="button")


class IletisimveEngelliDurumBilgileriForm(JsonForm):
    class Meta:
        title = 'Bilgi Kontrol Ekranı'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."
        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": "Adres Bilgileri",
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
                        "group_title": "İletişim Bilgileri",
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
                        "group_title": "Engel Bilgileri",
                        "items": ['engelli_durumu', 'engel_grubu', 'engel_derecesi', 'engel_orani']
                    }
                ]
            }
        ]

    ikamet_adresi = fields.Text("İkamet Adresi")
    ikamet_il = fields.String("İkamet Il")
    ikamet_ilce = fields.String("İkamet Ilce")
    adres_2 = fields.String("Adres 2")
    adres_2_posta_kodu = fields.String("Adres 2 Posta Kodu")
    oda_tel_no = fields.String("Oda Telefon Numarası")
    cep_telefonu = fields.String("Cep Telefonu")
    e_posta = fields.String("Kurum E-Posta(Yeni Personel için boş bırakınız)", required=False)
    e_posta_2 = fields.String("E-Posta 2")
    e_posta_3 = fields.String("E-Posta 3")
    web_sitesi = fields.String("Web Sitesi")
    notlar = fields.Text("Not")
    engelli_durumu = fields.String("Engellilik")
    engel_grubu = fields.String("Engel Grubu")
    engel_derecesi = fields.String("Engel Derecesi")
    engel_orani = fields.Integer("Engellilik Orani")
