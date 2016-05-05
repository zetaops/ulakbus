# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from datetime import date

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models.hitap.hitap_sebep import HitapSebep
from ulakbus.models.hitap.hitap import HizmetKayitlari
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models.personel import Personel, Atama, Kadro


class PersonelAtama(CrudView):
    class Meta:
        model = 'Personel'

    def eksik_bilgileri_kontrol_et(self):

        try:
            personel = Personel.objects.get(self.input['id'])
        except KeyError:
            personel = Personel.objects.get(self.current.task_data['personel_id'])

        self.current.task_data['personel_id'] = personel.key
        self.current.task_data['personel_ad'] = personel.ad
        self.current.task_data['personel_soyad'] = personel.soyad
        if personel.kurum_sicil_no_int:
            self.current.task_data['eksik_bilgi_yok'] = True
        else:
            self.current.task_data['eksik_bilgi_yok'] = False
            self.current.task_data['ilk_atama'] = True

    def eksik_bilgi_form(self):
        _form = EksikBilgiForm(current=self.current)
        if 'hata_msg' in self.current.task_data:
            _form.help_text = self.current.task_data['hata_msg']

        son_personel = Personel.objects.set_params(sort='kurum_sicil_no_int desc')[0]
        personel = Personel.objects.get(self.current.task_data['personel_id'])

        _form.kurum_sicil_no_int = fields.Integer("Kurum Sicil No (Sıradaki Sicil No : KON-%s)" %
                                                  str(son_personel.kurum_sicil_no_int + 1),
                                                  required=True,
                                                  default=son_personel.kurum_sicil_no_int + 1)

        _form.personel_turu = fields.Integer("Personel Tipi", choices="personel_turu",
                                            default=personel.personel_turu)
        _form.unvan = fields.Integer("Personel Unvan", choices="unvan_kod", required=False,
                                     default=personel.unvan)
        _form.emekli_sicil_no = fields.String("Emekli Sicil No", default=personel.emekli_sicil_no)
        _form.hizmet_sinif = fields.Integer("Hizmet Sınıfı", choices="hizmet_sinifi",
                                            default=personel.hizmet_sinifi)
        _form.statu = fields.Integer("Statü", choices="personel_statu", default=personel.statu)
        _form.brans = fields.String("Branş", default=personel.brans)
        _form.gorev_suresi_baslama = fields.Date("Görev Süresi Başlama",
                                                 default=str(personel.gorev_suresi_baslama))
        _form.gorev_suresi_bitis = fields.Date("Görev Süresi Bitiş",
                                               default=str(personel.gorev_suresi_bitis))
        _form.goreve_baslama_tarihi = fields.Date("Göreve Başlama Tarihi",
                                                  default=str(personel.goreve_baslama_tarihi))

        _form.baslama_sebep = fields.String("Durum", type='typeahead')
        _form.baslama_sebep.default = str(personel.baslama_sebep)
        # TODO: Set choices key error fırlatıyor. düzeltilecek
        # _form.set_choices_of('baslama_sebep', choices=prepare_choices_for_model(HitapSebep, nevi=1))

        _form.mecburi_hizmet_suresi = fields.Date("Mecburi Hizmet Süresi",
                                                  default=str(personel.mecburi_hizmet_suresi))
        _form.emekli_giris_tarihi = fields.Date("Emekliliğe Giriş Tarihi",
                                                default=str(personel.emekli_giris_tarihi))

        self.form_out(_form)

    def eksik_bilgi_kaydet(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        # personel.kurum_sicil_no_int = self.current.input['form']['kurum_sicil_no_int']
        for key in self.current.input['form']:
            setattr(personel, key, self.current.input['form'][key])

        personel.save()

    def atama_durumunu_kontrol_et(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        self.current.task_data['personel'] = personel.clean_value()
        self.current.task_data['guncel_atama'] = personel.atama.key

        if personel.atama.key:
            self.current.task_data['ilk_atama'] = False
        else:
            self.current.task_data['ilk_atama'] = True

    def kadro_bilgileri_form(self):
        _form = KadroBilgiForm(current=self.current,
                               title="%s %s için Atama Yapılacak Kadroyu Seçin" %
                                     (self.current.task_data['personel_ad'],
                                      self.current.task_data['personel_soyad']))

        _form.set_choices_of('kadro', choices=prepare_choices_for_model(Kadro, durum=2))
        _form.set_choices_of('durum', choices=prepare_choices_for_model(HitapSebep, nevi=1))

        self.form_out(_form)

    def kadro_bilgileri_goster(self):
        genel_bilgiler = """**Adı**: {ad}
                           **Soyad**: {soyad}
                           **Personel Tipi**: {personel_turu}""".format(
            **self.current.task_data['personel'])
        atama = Atama.objects.get(self.current.task_data['guncel_atama'])
        atama_data = atama.clean_value()

        atama_bilgileri = "**Hizmet Sınıfı**:\n" \
                          "**Birim**: \n".format(**atama_data)

        output = [{'Genel Bilgiler': genel_bilgiler,
                   'Atama Bilgileri': atama_bilgileri}]

        self.current.output['object'] = {
            "type": "table-multiRow",
            "title": "Personel Atama Bilgileri",
            "fields": output,
            "actions": False
        }

        _form = JsonForm(current=self.current)
        _form.edit = fields.Button("Düzenle", cmd="edit")
        _form.yeni_atama = fields.Button("Atama Yap", cmd="yeni_atama", flow="yeni_atama",
                                         form_validation=False)
        self.form_out(_form)

    def atama_kaydet(self):
        atanacak_kadro = Kadro.objects.get(self.current.input['form']['kadro'])
        if not atanacak_kadro:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = "Kadro Dolu olduğu için atama yapılamaz."
        elif atanacak_kadro.durum != 2:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = "Kadro Dolu olduğu için atama yapılamaz."
        else:
            self.current.task_data['hata'] = False
            self.current.task_data['kadro'] = str(atanacak_kadro)

            atama = Atama(personel_id=self.current.task_data['personel_id'])
            try:
                atama.kadro = atanacak_kadro
                atama.ibraz_tarihi = self.current.input['form']['ibraz_tarihi']
                atama.durum_id = self.current.input['form']['durum']
                atama.nereden = self.current.input['form']['nereden']
                atama.atama_aciklama = self.current.input['form']['atama_aciklama']
                atama.goreve_baslama_tarihi = self.current.input['form']['goreve_baslama_tarihi']
                atama.goreve_baslama_aciklama = self.current.input['form'][
                    'goreve_baslama_aciklama']
                atama.save()

                personel = Personel.objects.get(self.current.task_data['personel_id'])

                hk = HizmetKayitlari(personel=personel)
                hk.baslama_tarihi = date.today()

                # TODO: Hizmet Kayitlari Model post_save düzgün çalışmadığı için eklendi. #5277
                # Düzeltildiğinde kaldırılacak
                hk.tckn = personel.tckn
                hk.hizmet_sinifi = personel.hizmet_sinifi
                hk.kadro_derece = atanacak_kadro.derece
                hk.odeme_derece = personel.gorev_ayligi_derece
                hk.odeme_kademe = personel.gorev_ayligi_kademe
                hk.odeme_ekgosterge = personel.gorev_ayligi_ekgosterge
                hk.kazanilmis_hak_ayligi_derece = personel.kazanilmis_hak_derece
                hk.kazanilmis_hak_ayligi_kademe = personel.kazanilmis_hak_kademe
                hk.kazanilmis_hak_ayligi_ekgosterge = personel.kazanilmis_hak_ekgosterge
                hk.emekli_derece = personel.emekli_muktesebat_derece
                hk.emekli_kademe = personel.emekli_muktesebat_kademe
                hk.emekli_ekgosterge = personel.emekli_muktesebat_ekgosterge

                hk.sebep_kod = atama.durum.sebep_no
                hk.kurum_onay_tarihi = self.current.input['form']['kurum_onay_tarihi']
                hk.sync = 1  # TODO: Düzeltilecek, beta boyunca senkronize etmemesi için 1 yapıldı
                hk.personel = personel
                hk.save()
            except:
                # Herhangi bir hata oluşursa atama silinecek
                atama.delete(True)

    def atama_goster(self):
        kisi_bilgileri = """**Adı**: {ad}
                           **Soyad**: {soyad}""".format(**self.current.task_data['personel'])

        atama_bilgileri = "**kadro**: {kadro}\n" \
                          "**İlçe**: \n".format(**self.current.task_data)

        output = [{'Kişi Bilgileri': kisi_bilgileri,
                   'Atama Bilgileri': atama_bilgileri}]

        self.current.output['object'] = {
            "type": "table-multiRow",
            "title": "Personel Ataması Başarı ile Tamamlandı",
            "fields": output,
            "actions": False
        }

        _form = JsonForm(current=self.current)

        _form.hitap = fields.Button("Hitap ile Eşleştir", cmd="hitap_getir", btn='hitap')
        _form.bitir = fields.Button("İşlemi Bitir", cmd="bitir", flow="bitir",
                                    form_validation=False)
        self.form_out(_form)

    def atama_iptal(self):
        self.current.output['msgbox'] = {
            'type': 'error', "title": 'Atama İptal Edildi',
            "msg": 'Personel atama işlemi İptal edildi.'
        }

    def sonuc_bilgisi_goster(self):
        hitap_sonuc = ''
        if 'hitap_tamam' in self.current.task_data:
            if self.current.task_data['hitap_tamam']:
                hitap_sonuc = 'Personel için hitap bilgileri Hitap sunucusu ile eşleştirildi.'
            else:
                hitap_sonuc = """
                    Personel için hitap bilgileri Hitap sunucusu ile eşleştirilemedi!!
                    Bu işlemi daha sonra tekrar başlatabilirsiniz.
                    """

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Personel Atama Başarılı',
            "msg": 'Atama İşlemi Başarıyla gerçekleştirildi. ' + hitap_sonuc
        }

    def hitap_bilgi_getir(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        from ulakbus.services.zato_wrapper import HitapHizmetCetveliSenkronizeEt
        hizmet_cetveli = HitapHizmetCetveliSenkronizeEt(tckn=str(personel.tckn))

        try:
            response = hizmet_cetveli.zato_request()
            self.current.task_data['hitap_tamam'] = True
        except:
            self.current.task_data['hitap_tamam'] = False

        self.current.set_message(
            title='%s TC no için Hitap Hizmet cetveli eşitlendi' % personel.tckn, msg='', typ=1)

    def hatayi_gozden_gecir(self):
        if self.current.task_data['hata_msg']:
            msg = self.current.task_data['hata_msg']
        else:
            msg = "Bilinmeyen bir hata oluştu :( sebebini biliyorsanız bizede söyleyinde düzeltelim"
        self.current.output['msgbox'] = {
            'type': 'error', "title": 'İşlem Başarısız',
            "msg": msg
        }

        _form = JsonForm(current=self.current)
        _form.tekrar = fields.Button("Tekrar Dene", style="btn-success", cmd="tekrar")
        _form.iptal = fields.Button("İptal", cmd="iptal")
        self.form_out(_form)


class EksikBilgiForm(JsonForm):
    class Meta:
        title = 'Eksik Personel Bilgileri'
        help_text = "Atama Öncesi Personelin Eksik Bilgilerini Düzenle."

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": "Genel Bilgiler",
                        "items": ['kurum_sicil_no_int', 'personel_turu', 'unvan',
                                  'hizmet_sinif', 'statu', 'brans', 'emekli_sicil_no',
                                  'emekli_giris_tarihi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": "Çalıştığı birimde işe başlama",
                        "items": ['mecburi_hizmet_suresi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": "Görev Süresi",
                        "items": ['gorev_suresi_baslama', 'gorev_suresi_bitis',
                                  'engel_derecesi', 'engel_orani', 'baslama_sebep',
                                  'goreve_baslama_tarihi']
                    }
                ]
            }
        ]

    baslama_sebep = None

    kaydet = fields.Button("Kaydet", cmd="kaydet", style="btn-success")
    iptal = fields.Button("İptal", cmd="iptal", flow="iptal", form_validation=False)


class KadroBilgiForm(JsonForm):
    class Meta:
        title = 'Atama Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    kadro = fields.String("Atanacak Kadro Seçiniz", type='typeahead')
    ibraz_tarihi = fields.Date("İbraz Tarihi")
    durum = fields.String("Durum", type='typeahead')
    nereden = fields.Integer("Nereden")
    atama_aciklama = fields.Text("Atama Açıklama")
    goreve_baslama_tarihi = fields.Date("Birimde Göreve Başlama Tarihi")
    goreve_baslama_aciklama = fields.String("Birimde Göreve Başlama Açıklama")
    kurum_onay_tarihi = fields.Date("Kurum Onay Tarihi")

    kaydet = fields.Button("Kaydet", cmd="kaydet", style="btn-success")
    iptal = fields.Button("İptal", cmd="iptal", flow="iptal", form_validation=False)
