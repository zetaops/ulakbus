# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from collections import OrderedDict
from datetime import date

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models.hitap.hitap_sebep import HitapSebep
from ulakbus.models.hitap.hitap import HizmetKayitlari
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy
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

        # son_personel = Personel.objects.set_params(sort='kurum_sicil_no_int desc')[0]
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        _form.kurum_sicil_no_int = fields.Integer(_(u"Kurum Sicil No"), default=personel.kurum_sicil_no_int)
        _form.personel_turu = fields.Integer(_(u"Personel Tipi"), choices="personel_turu",
                                             default=personel.personel_turu)
        _form.unvan = fields.Integer(_(u"Personel Unvan"), choices="unvan_kod", required=False,
                                     default=personel.unvan)
        _form.emekli_sicil_no = fields.String(_(u"Emekli Sicil No"), default=personel.emekli_sicil_no)
        _form.hizmet_sinif = fields.Integer(_(u"Hizmet Sınıfı"), choices="hizmet_sinifi",
                                            default=personel.hizmet_sinifi)
        _form.statu = fields.Integer(_(u"Statü"), choices="personel_statu", default=personel.statu)
        _form.brans = fields.String(_(u"Branş"), default=personel.brans)
        _form.gorev_suresi_baslama = fields.Date(_(u"Görev Süresi Başlama"),
                                                 default=str(personel.gorev_suresi_baslama))
        _form.gorev_suresi_bitis = fields.Date(_(u"Görev Süresi Bitiş"),
                                               default=str(personel.gorev_suresi_bitis))
        _form.goreve_baslama_tarihi = fields.Date(_(u"Göreve Başlama Tarihi"),
                                                  default=str(personel.goreve_baslama_tarihi))

        _form.baslama_sebep = fields.String(_(u"Durum")) #typeahead olacak
        _form.baslama_sebep.default = str(personel.baslama_sebep)
        # TODO: Set choices key error fırlatıyor. düzeltilecek
        _form.set_choices_of('baslama_sebep', choices=prepare_choices_for_model(HitapSebep, nevi=1))

        _form.mecburi_hizmet_suresi = fields.Date(_(u"Mecburi Hizmet Süresi"),
                                                  default=str(personel.mecburi_hizmet_suresi))
        _form.emekli_giris_tarihi = fields.Date(_(u"Emekliliğe Giriş Tarihi"),
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
                               title="%(ad)s %(soyad)s adlı personelin kadro bilgilerini doldurunuz." % {
                                   'ad': self.current.task_data['personel_ad'],
                                   'soyad': self.current.task_data['personel_soyad'],
                               })

        _form.set_choices_of('kadro', choices=prepare_choices_for_model(Kadro, durum=2))
        _form.set_choices_of('durum', choices=prepare_choices_for_model(HitapSebep, nevi=1))

        self.form_out(_form)

    def kadro_bilgileri_goster(self):
        genel_bilgiler = _("""**Adı**: {ad}
                              **Soyadı**: {soyad}
                              **Personel Tipi**: {personel_turu}""").format(**self.current.task_data['personel'])
        atama = Atama.objects.get(self.current.task_data['guncel_atama'])
        atama_verileri = atama.clean_value()
        birim = Kadro.objects.get(atama_verileri["kadro_id"]).birim()
        atama_bilgileri = _("**Hizmet Sınıfı**: {hizmet_sinifi}\n**Birim**:{0}\n").format(birim, **atama_verileri)

        output = [{0: _(u'Genel Bilgiler'),
                   1: _(u'Atama Bilgileri')}]
        self.current.output['objects'] = output
        bilgiler = OrderedDict([(0, genel_bilgiler), (1, atama_bilgileri)])
        item = {
            "type": "table-multiRow",
            "fields": bilgiler,
            "actions": False
        }
        self.current.output['objects'].append(item)
        _form = JsonForm(current=self.current, title=_(u"Personel Atama Bilgileri"))
        _form.edit = fields.Button(_("Düzenle"), cmd="edit")
        _form.yeni_atama = fields.Button(_("Atama Yap"), cmd="yeni_atama", form_validation=False)
        self.form_out(_form)

    def atama_kaydet(self):
        atanacak_kadro = Kadro.objects.get(self.current.input['form']['kadro'])
        if not atanacak_kadro:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = _(u"Kadro Dolu olduğu için atama yapılamaz.")
        elif atanacak_kadro.durum != 2:
            self.current.task_data['hata'] = True
            self.current.task_data['hata_msg'] = _(u"Kadro Dolu olduğu için atama yapılamaz.")
        else:
            self.current.task_data['hata'] = False
            self.current.task_data['kadro'] = str(atanacak_kadro)

            atama = Atama(personel_id=self.current.task_data['personel_id'])
            try:
                atama.kadro = atanacak_kadro
                atama.ibraz_tarihi = self.current.input['form']['ibraz_tarihi']
                atama.durum = HitapSebep.objects.get(self.current.input['form']['durum'])
                atama.nereden = self.current.input['form']['nereden']
                atama.atama_aciklama = self.current.input['form']['atama_aciklama']
                atama.goreve_baslama_tarihi = self.current.input['form']['goreve_baslama_tarihi']
                atama.goreve_baslama_aciklama = self.current.input['form'][
                    'goreve_baslama_aciklama']
                atama.save()

                personel = Personel.objects.get(self.current.task_data['personel_id'])
                hk = HizmetKayitlari(personel=personel)
                hk.baslama_tarihi = date.today()
                hk.kurum_onay_tarihi = self.current.input['form']['kurum_onay_tarihi']
                hk.sync = 1  # TODO: Düzeltilecek, beta boyunca senkronize etmemesi için 1 yapıldı
                hk.save()
            except Exception as e:
                # Herhangi bir hata oluşursa atama silinecek
                atama.delete()
                self.current.output['msgbox'] = {
                    'type': 'warning', "title": _(u'Bir Hata Oluştu'),
                    "msg": _(u'%s') % e.message
                }

    def atama_goster(self):
        kisi_bilgileri = _("""**Adı**: {ad}
                              **Soyad**: {soyad}""").format(**self.current.task_data['personel'])

        atama_bilgileri = _("**Kadro**: {kadro}\n" \
                            "**İlçe**: \n").format(**self.current.task_data)

        # output = [{_(u'Kişi Bilgileri'): kisi_bilgileri,
        #            _(u'Atama Bilgileri'): atama_bilgileri}]

        output = [{0: _(u'Kişi Bilgileri'),
                   1: _(u'Atama Bilgileri')}]
        self.current.output['objects'] = output
        bilgiler = OrderedDict([(0, kisi_bilgileri), (1, atama_bilgileri)])
        item = {
            "type": "table-multiRow",
            "title": _(u"Personel Ataması Başarı ile Tamamlandı"),
            "fields": bilgiler,
            "actions": False
        }
        self.current.output['objects'].append(item)

        _form = JsonForm(current=self.current, title="Kişi ve Atama Bilgileri")

        _form.hitap = fields.Button(_(u"Hitap ile Eşleştir"), cmd="hitap_getir", btn='hitap')
        _form.bitir = fields.Button(_(u"İşlemi Bitir"), cmd="bitir", flow="bitir",
                                    form_validation=False)
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def atama_iptal(self):
        self.current.output['msgbox'] = {
            'type': 'error', "title": _(u'Atama İptal Edildi'),
            "msg": _(u'Personel atama işlemi İptal edildi.'),
        }

    def sonuc_bilgisi_goster(self):
        hitap_sonuc = ''
        if 'hitap_tamam' in self.current.task_data:
            if self.current.task_data['hitap_tamam']:
                hitap_sonuc = _(u'Personel için hitap bilgileri Hitap sunucusu ile eşleştirildi.')
            else:
                hitap_sonuc = _(u"""
                    Personel için hitap bilgileri Hitap sunucusu ile eşleştirilemedi!!
                    Bu işlemi daha sonra tekrar başlatabilirsiniz.
                    """)

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Personel Atama Başarılı'),
            "msg": _(u'Atama İşlemi Başarıyla gerçekleştirildi. ') + hitap_sonuc
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
            title=_(u'%s TC no için Hitap Hizmet cetveli eşitlendi') % personel.tckn, msg='', typ=1)

    def hatayi_gozden_gecir(self):
        if self.current.task_data['hata_msg']:
            msg = self.current.task_data['hata_msg']
        else:
            msg = _(u"Bilinmeyen bir hata oluştu :( sebebini biliyorsanız bizede söyleyinde düzeltelim")
        self.current.output['msgbox'] = {
            'type': 'error', "title": _(u'İşlem Başarısız'),
            "msg": msg
        }

        _form = JsonForm(current=self.current)
        _form.tekrar = fields.Button(_(u"Tekrar Dene"), style="btn-success", cmd="tekrar")
        _form.iptal = fields.Button(_(u"İptal"), cmd="iptal")
        self.form_out(_form)


class EksikBilgiForm(JsonForm):
    class Meta:
        title = _(u'Eksik Personel Bilgileri')
        help_text = _(u"Atama Öncesi Personelin Eksik Bilgilerini Düzenle.")

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": _(u"Genel Bilgiler"),
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
                        "group_title": _(u"Çalıştığı birimde işe başlama"),
                        "items": ['mecburi_hizmet_suresi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": _(u"Görev Süresi"),
                        "items": ['gorev_suresi_baslama', 'gorev_suresi_bitis',
                                  'engel_derecesi', 'engel_orani', 'baslama_sebep',
                                  'goreve_baslama_tarihi']
                    }
                ]
            }
        ]

    baslama_sebep = None

    kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet", style="btn-success")
    iptal = fields.Button(_(u"İptal"), cmd="iptal", flow="iptal", form_validation=False)


class KadroBilgiForm(JsonForm):
    class Meta:
        title = gettext_lazy(u'Atama Bilgileri')

    kadro = fields.String(_(u"Atanacak Kadro Seçiniz"))  # typeahead olacak
    ibraz_tarihi = fields.Date(_(u"İbraz Tarihi"))
    durum = fields.String(_(u"Durum"))  # typeahead olacak
    nereden = fields.Integer(_(u"Nereden"))
    atama_aciklama = fields.Text(_(u"Atama Açıklama"))
    goreve_baslama_tarihi = fields.Date(_(u"Göreve Başlama Tarihi"))
    goreve_baslama_aciklama = fields.String(_(u"Göreve Başlama Açıklama"))
    kurum_onay_tarihi = fields.Date(_(u"Kurum Onay Tarihi"))

    kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet", style="btn-success")
    iptal = fields.Button(_(u"İptal"), cmd="iptal", flow="iptal", form_validation=False)
