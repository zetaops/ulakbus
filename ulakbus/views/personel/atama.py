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
from ulakbus.models.hitap.hitap import HitapSebep
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models.personel import Personel, Atama, Kadro

class PersonelAtama(CrudView):
    class Meta:
        model = 'Personel'

    def eksik_bilgileri_kontrol_et(self):
        try:
            personel = Personel.objects.get(self.input['id'])
        except:
            personel = Personel.objects.get(self.current.task_data['personel_id'])

        self.current.task_data['personel_id'] = personel.key
        self.current.task_data['personel_ad'] = personel.ad
        self.current.task_data['personel_soyad'] = personel.soyad
        if personel.kurum_sicil_no_int:
            self.current.task_data['eksik_bilgi_yok'] = True
        else:
            self.current.task_data['eksik_bilgi_yok'] = False

    def eksik_bilgi_form(self):
        _form = EksikBilgiForm(current=self.current)
        if 'hata_msg' in self.current.task_data:
            _form.help_text = self.current.task_data['hata_msg']

        son_personel = Personel.objects.set_params(sort='kurum_sicil_no_int desc')[0]
        personel =  Personel.objects.get(self.current.task_data['personel_id'])

        _form.sicil_no = fields.Integer("Kurum Sicil No (Sıradaki Sicil No : KON-%s)" %
                                        str(son_personel.kurum_sicil_no_int+1),
                                        required=True,default=son_personel.kurum_sicil_no_int+1)

        _form.unvan = fields.Integer("Personel Unvan", choices="unvan_kod", required=False,default=personel.unvan)
        _form.emekli_sicil_no = fields.String("Emekli Sicil No",default=personel.emekli_sicil_no)
        _form.personel_tip = fields.Integer("Personel Tipi", choices="personel_tip",default=personel.personel_tip)
        _form.hizmet_sinif = fields.Integer("Hizmet Sınıfı", choices="hizmet_sinifi",default=personel.hizmet_sinifi)
        _form.statu = fields.Integer("Statü", choices="personel_statu",default=personel.statu)
        _form.brans = fields.String("Branş",default=personel.brans)
        _form.gorev_suresi_baslama = fields.Date("Görev Süresi Başlama", format="%d.%m.%Y",default=personel.gorev_suresi_baslama)
        _form.gorev_suresi_bitis = fields.Date("Görev Süresi Bitiş", format="%d.%m.%Y",default=personel.gorev_suresi_bitis)
        _form.goreve_baslama_tarihi = fields.Date("Göreve Başlama Tarihi", format="%d.%m.%Y",default=personel.goreve_baslama_tarihi)
        _form.baslama_sebep = fields.String("Durum",personel.baslama_sebep)
        _form.set_choices_of('baslama_sebep', choices=prepare_choices_for_model(HitapSebep, durum=1))
        _form.mecburi_hizmet_suresi = fields.Date("Mecburi Hizmet Süresi", format="%d.%m.%Y",default=personel.mecburi_hizmet_suresi)
        _form.emekli_giris_tarihi = fields.Date("Emekliliğe Giriş Tarihi", format="%d.%m.%Y",default=personel.emekli_giris_tarihi)


        self.form_out(_form)

    def eksik_bilgi_kaydet(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        personel.kurum_sicil_no_int = self.current.input['form']['sicil_no']
        personel.save()

    def atama_durumunu_kontrol_et(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        atama = Atama.objects.filter(personel=personel)
        if atama:
            self.current.task_data['atanabilir'] = False
            self.current.task_data['hata_msg'] = "Seçili Personelin ataması daha önce yapılmış. Açığa alınmadan yeni atama yapılamaz"
        else:
            self.current.task_data['atanabilir'] = True

    def kadro_bilgileri_form(self):
        _form = KadroBilgiForm(current=self.current,
                         title="%s %s için Atama Yapılacak Kadroyu Seçin" %
                               (self.current.task_data['personel_ad'],
                                self.current.task_data['personel_soyad']))


        _form.set_choices_of('kadro', choices=prepare_choices_for_model(Kadro, durum=2))

        self.form_out(_form)

    def atama_kaydet(self):
        atanacak_kadro = Kadro.objects.get(self.current.input['form']['kadro'])
        if not atanacak_kadro:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = "Kadro Dolu olduğu için atama yapılamaz."
        elif atanacak_kadro.durum!=2:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = "Kadro Dolu olduğu için atama yapılamaz."
        else:
            self.current.task_data['hata'] = False
            self.current.task_data['kadro'] = str(atanacak_kadro)

            atama = Atama(personel_id = self.current.task_data['personel_id'])
            atama.kadro = atanacak_kadro
            atama.save()

    def atama_goster(self):
        kisi_bilgileri = """**Adı**: {personel_ad}
                           **Soyad**: {personel_soyad}""".format(**self.current.task_data)

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
        _form.bitir = fields.Button("İşlemi Bitir", cmd="bitir", flow="bitir", form_validation=False)
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
                hitap_sonuc = 'Personel için hitap bilgileri Hitap sunucusu ile eşleştirilemedi !! Bu işlemi daha sonra tekrar başlatabilirsiniz.'

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Personel Atama Başarılı',
            "msg": 'Atama İşlemi Başarıyla gerçekleştirildi. ' + hitap_sonuc
        }

    def hitap_bilgi_getir(self):
        ## TODO: Kontol edilecek
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        # mernis servisi henuz hazir degil
        from ulakbus.services.zato_wrapper import HitapHizmetCetveliGetir,HitapHizmetCetveliSenkronizeEt
        hizmet_cetveli = HitapHizmetCetveliSenkronizeEt(tckn=str(personel.tckn))
        try:
            response = hizmet_cetveli.zato_request()
            self.current.task_data['hitap_tamam'] = True
        except:
            self.current.task_data['hitap_tamam'] = False

        self.current.set_message(title='%s TC no için Hitap Hizmet cetveli eşitlendi' % personel.tckn,
                                 msg='', typ=1, url="/wftoken/%s" % self.current.token)

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

    """
    _form.atama_yapma = fields.Boolean("Atama Yapmadan Kaydet", flow="atama_yapmadan_gec", cmd="atama_yapmadan_gec",
                                       type='confirm',
                                       confirm_message='Atama yapmadan kaydetmek istediğinize eminmisiniz?')
    """

## Formlar
class EksikBilgiForm(JsonForm):
    class Meta:
        title = 'Eksik Personel Bilgileri'
        help_text = "Atama Öncesi Personelin Eksik Bilgilerini Düzenle."

    kaydet = fields.Button("Kaydet", cmd="kaydet", style="btn-success")
    iptal = fields.Button("İptal", cmd="iptal", flow="iptal", form_validation=False)

class KadroBilgiForm(JsonForm):
    class Meta:
        title = 'Atama Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    kadro = fields.String("Atanacak Kadro Seçiniz", type='typeahead')
    kaydet = fields.Button("Kaydet", cmd="kaydet", style="btn-success")
    iptal = fields.Button("İptal", cmd="iptal", flow="iptal", form_validation=False)
