# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from ulakbus.lib.view_helpers import prepare_titlemap_for_model, prepare_choices_for_model
from zengine.views.crud import CrudView, form_modifier

from zengine.forms import JsonForm, fields
from ulakbus.models.personel import Kadro
from collections import OrderedDict
from ulakbus.models.personel import Personel


# Views
class YeniPersonelEkle(CrudView):
    class Meta:
        model = 'Personel'

    def yeni_personel_form(self):
        _form = YeniPersonelTcknForm(current=self.current)
        self.form_out(_form)

    def hitap_bilgileri_getir(self):
        tckn = str(self.current.input['form']['tckn'])
        # mernis servisi henuz hazir degil
        #        from ulakbus.services.zato_wrapper import HitapHizmetCetveliGetir
        #        hizmet_cetveli = HitapHizmetCetveliGetir(tckn=tckn)
        #        response = hizmet_cetveli.zato_request()
        # bu sebeple response elle olusturuyoruz.

        # response = {"ad": "Kamil", "soyad": "Soylu", "tckn": "12345678900", "dogum_yeri": "Afyon",
        #            "dogum_tarihi": "10.10.1940"}
        self.current.task_data['hitap_tamam'] = True
        self.current.task_data['hizmet_cetveli'] = {}  # response
        self.current.task_data['tckn'] = tckn

        self.current.set_message(title='%s TC no için Hitap servisi başlatıldı' % tckn,
                                 msg='', typ=1, url="/wftoken/%s" % self.current.token)

    def mernis_kimlik_bilgileri_getir(self):
        tckn = self.current.input['form']['tckn']

        # Personelin daha önce bulunup bulunmadığını kontrol et
        try:
            Personel.objects.get(tckn=tckn)
            self.current.task_data['mernis_tamam'] = False
            self.current.task_data['hata_msg'] = "Personel Daha Önce Kaydedilmiş"
        except:
            from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir, MernisCuzdanBilgileriGetir
            mernis_bilgileri = MernisKimlikBilgileriGetir(tckn=str(tckn))
            response = mernis_bilgileri.zato_request()
            self.current.task_data['mernis_tamam'] = True
            self.current.task_data['kimlik_bilgileri'] = response
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
        # mernis servisi henuz hazir degil
        from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
        mernis_bilgileri = KPSAdresBilgileriGetir(tckn=str(tckn))
        response = mernis_bilgileri.zato_request()
        # bu sebeple response elle olusturuyoruz.
        # response = {"il": "Konya", "ilce": "Meram", "adres": "Meram Caddesi No4 Meram Konya"}

        self.current.task_data['adres_tamam'] = True
        self.current.task_data['adres_bilgileri'] = response

        return response

    def yeni_ekle_kontrol(self):
        _form = JsonForm(current=self.current, title="Bilgi Kontrol Ekranı")

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Personel Kayıt Uyarısı',
            "msg": 'Lütfen Personel bilgilerinin doğruluğunu kontrol ediniz. Kayıt işlemi geri döndürülemez.'
        }
        _form.kaydet = fields.Button("Kaydet (Bu işlem geri alınamaz!)", cmd="kaydet", btn='success')
        _form.iptal = fields.Button("İptal", cmd="iptal", flow="iptal")

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

    def hata_goster(self):
        if self.current.task_data['hata_msg']:
            msg = self.current.task_data['hata_msg']
        else:
            msg = "Bilinmeyen bir hata oluştu :( sebebini biliyorsanız bizede söyleyinde düzeltelim"
        self.current.output['msgbox'] = {
            'type': 'error', "title": 'İşlem Başarısız',
            "msg": msg
        }

class IletisimveEngelliDurumBilgileri(CrudView):
    def show_view(self):
        mernis_adres = ""  # mernis_adres_bilgileri_getir(self.current.input['tckn'])
        form = IletisimveEngelliDurumBilgileriForm()
        form.ikamet_adresi = mernis_adres['adres']
        form.il = mernis_adres['il']
        form.ilce = mernis_adres['ilce']
        self.current.output['forms'] = form.serialize()

    def do_view(self):
        pass


class Atama(CrudView):
    class Meta:
        model = 'Atama'

    def kadro_sec_form(self):
        _form = JsonForm(current=self.current,
                         title="%s %s için Atama Yapılacak Kadroyu Seçin" %
                               (self.current.task_data['kimlik_bilgileri']['ad'],
                                self.current.task_data['kimlik_bilgileri']['soyad']))
        _form.kadro = fields.Integer("Atanacak Kadro Seçiniz", type='typeahead')
        self.choices = prepare_titlemap_for_model(Kadro, durum=2)

        _form.sec = fields.Button("Seç", flow="sec", cmd="sec")
        _form.atama_yapma = fields.Boolean("Atama Yapmadan Kaydet", flow="atama_yapmadan_gec", cmd="atama_yapmadan_gec",
                                           type='confirm',
                                           confirm_message='Atama yapmadan kaydetmek istediğinize eminmisiniz?')
        self.form_out(_form)

    @form_modifier
    def change_form_elements(self, serialized_form):
        """
        This function edits form elements as can be understood from the name of its decorator
        :param serialized_form:
        """
        if 'kadro' in serialized_form['schema']['properties']:
            serialized_form['schema']['properties']['kadro']['titleMap'] = self.choices

    def iptal(self):
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Atama İptal Edildi',
            "msg": 'Yeni personel atama işlemi İptal edildi.'
        }


# Formlar
class YeniPersonelTcknForm(JsonForm):
    class Meta:
        title = 'Yeni Personel Ekle'
        help_text = "Kimlik Numarası ile MERNIS ve HITAP bilgileri getir."

    tckn = fields.String("TC No")
    cmd = fields.String("Bilgileri Getir", type="button")


class KimlikBilgileriForm(JsonForm):
    class Meta:
        title = 'Yeni Personel Ekle'
        help_text = "Kimlik Numarası ile MERNIS ve HITAP bilgileri getir."

    tckn = fields.String("TC No")
    ad = fields.String("Adı")
    soyad = fields.String("Soyadı")
    cinsiyet = fields.String("Cinsiyet")
    uyruk = fields.String("Uyruk")
    cuzdan_seri = fields.String("Seri")
    cuzdan_seri_no = fields.String("Seri No")
    baba_adi = fields.String("Ana Adi")
    ana_adi = fields.String("Baba Adi")
    dogum_tarihi = fields.Date("Doğum Tarihi")
    dogum_yeri = fields.String("Doğum Yeri")
    medeni_hali = fields.String("Medeni Hali")
    kayitli_oldugu_il = fields.String("Il", )
    kayitli_oldugu_ilce = fields.String("Ilce")
    kayitli_oldugu_mahalle_koy = fields.String("Mahalle/Koy")
    kayitli_oldugu_cilt_no = fields.String("Cilt No")
    kayitli_oldugu_aile_sira_no = fields.String("Aile Sira No")
    kayitli_oldugu_sira_no = fields.String("Sira No")
    kimlik_cuzdani_verildigi_yer = fields.String("Cuzdanin Verildigi Yer")
    kimlik_cuzdani_verilis_nedeni = fields.String("Cuzdanin Verilis Nedeni")
    kimlik_cuzdani_kayit_no = fields.String("Cuzdan Kayit No")
    kimlik_cuzdani_verilis_tarihi = fields.String("Cuzdan Kayit Tarihi")
    cmd = fields.Button("Kaydet")


class IletisimveEngelliDurumBilgileriForm(JsonForm):
    class Meta:
        title = 'Iletisim Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    ikamet_il = fields.String("İkamet Il")
    ikamet_ilce = fields.String("İkamet Ilce")
    ikamet_adresi = fields.String("İkamet Adresi")
    adres_2 = fields.String("Adres 2")
    adres_2_posta_kodu = fields.String("Adres 2 Posta Kodu", index=True)
    oda_tel_no = fields.String("Oda Telefon Numarası")
    cep_telefonu = fields.String("Cep Telefonu")
    e_posta = fields.String("E-Posta")
    e_posta_2 = fields.String("E-Posta")
    e_posta_3 = fields.String("E-Posta")
    web_sitesi = fields.String("Web Sitesi")
    notlar = fields.Text("Not")
    engelli_durumu = fields.String("Engellilik")
    engel_grubu = fields.String("Engel Grubu")
    engel_derecesi = fields.String("Engel Derecesi")
    engel_orani = fields.Integer("Engellilik Orani")

    # getir = fields.String("Adres Bilgileri Getir")
    cmd = fields.String("Kaydet")


class AtamaForm(JsonForm):
    class Meta:
        title = 'Iletisim Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    kurum_sicil_no = fields.String("Kurum Sicil No")
    personel_tip = fields.Integer("Personel Tip")
    hizmet_sinifi = fields.Integer("Hizmet Sinifi")
    emekli_sicil_no = fields.String("Emekli Sicil No")
    emekli_giris_tarihi = fields.String("Emekli Giris Tarihi")
    statu = fields.String("Statu")
    brans = fields.String("Brans")
    birim = fields.String("birim")

    kurumda_ise_baslama_tarihi = fields.String("Tarih")
    kurumda_ise_baslama_durumu = fields.String("Durum")

    calistigi_birimde_ise_baslama_tarihi = fields.String("Calistigi Birimde Ise Baslama Tarihi")
    calistigi_birimde_ise_baslama_ibraz_tarihi = fields.String("Ibraz Tarihi")
    calistigi_birimde_ise_baslama_durum = fields.String("Durum")
    calistigi_birimde_ise_baslama_aciklama = fields.String("Aciklama")
    calistigi_birimde_ise_baslama_nereden = fields.String("Nereden")
    calistigi_birimde_ise_baslama_mecburi_hizmet = fields.String("Mecburi Hizmet Tarihi")

    gorev_suresi_baslama = fields.Date("Gorev Suresi Baslama Tarihi")
    gorev_suresi_bitis = fields.Date("Bitis Tarihi")
    gorev_suresi_aciklama = fields.String("Aciklama")

    atama_yapilan_kadro = Kadro("Kadro")
    atama_yapilan_kadro_tarih = fields.Date("Kadro Tarih")
    atama_yapilan_kadro_derece = fields.Integer("Kadro Derece")
    atama_yapilan_kadro_derece_tarih = fields.Date("Kadro Derece Tarih")
    atama_yapilan_kadro_unvan = fields.String("Kadro Unvan")
    atama_yapilan_kadro_unvan_tarih = fields.String("Kadro Unvan Tarih")

    atama_gorev_ayligi_derece = fields.String("Derce")
    atama_gorev_ayligi_kademe = fields.String("Kademe")
    atama_gorev_ayligi_ek_gosterge = fields.String("Ek Gosterge")
    atama_gorev_ayligi_terfi_tarihi = fields.String("Terfi Tarihi")

    atama_kazanilmis_hak_ayligi_derece = fields.String("Derece")
    atama_kazanilmis_hak_ayligi_kademe = fields.String("Kademe")
    atama_kazanilmis_hak_ayligi_ek_gosterge = fields.String("Ek Gosterge")
    atama_kazanilmis_hak_ayligi_terfi_tarihi = fields.String("Terfi Tarihi")

    atama_emekli_muk_derece = fields.String("İkamet Il")
    atama_emekli_muk_kademe = fields.String("İkamet Il")
    atama_emekli_muk_ek_gosterge = fields.String("İkamet Il")
    atama_emekli_muk_terfi_tarihi = fields.String("İkamet Il")

    cmd = fields.Button("Kaydet")
