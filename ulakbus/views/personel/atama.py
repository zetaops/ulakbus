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

from ulakbus.models import Unit, ListNode
from pyoko.exceptions import ValidationError
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models.hitap.hitap_sebep import HitapSebep
from ulakbus.models.hitap.hitap import HizmetKayitlari
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.models.personel import Personel, Atama, Kadro

personel_bilgileri = """__Kurum Sicil No__: {kurum_sicil_no_int}


__Personel Tip__: {personel_turu} || __Aday Memur__:  {aday_memur} || __Hizmet Sınıfı__: {hizmet_sinifi}

__Emekli Sicil No__: {emekli_sicil_no} || __Emekli Giriş Tarihi__: {emekli_giris_tarihi}

__Statü__:  {statu} || __Branş__: {brans}

__Kurumda İşe Başlama Tarihi__: {kurumda_ise_baslama_tarihi}

__Durum__: {kurum_durum}

"""
calistigi_birim = """__Tarih__:  {goreve_baslama_tarihi} || __İbraz Tarihi__: {ibraz_tarihi}


__Durum__: {durum}

__Atama Açıklama__: {atama_aciklama}

__Nereden__:  {nereden}

__Birim__:  {birim}"""
kadro_unvan = """__Kadro No__:  {kadro_no} || __Tarihi__:  {kadro_derece_tarihi}


__Personel Ünvan__:  {unvan} || __Tarihi__:  {unvan_tarihi}

__Kadro Ünvan__:  {kadro} || __Tarihi__:  {kadro_tarihi} """

kadro_derece = """ __GA-Der__ /__GA-Kad__: {gorev_ayligi_derece} {gorev_ayligi_kademe} {gorunen_gorev_ayligi_kademe} || __Ek Gösterge__:  {gorev_ayligi_ekgosterge} || __Terfi Tarihi__:  {ga_sonraki_terfi_tarihi}


__KHA-Der__ /__KHA-Kad__: {kazanilmis_hak_derece} {kazanilmis_hak_kademe} {gorunen_kazanilmis_hak_kademe} || __Ek Gösterge__:  {kazanilmis_hak_ekgosterge} || __Terfi Tarihi__:  {kh_sonraki_terfi_tarihi}

__EM-Der__ /__EM-Kad__: {emekli_muktesebat_derece} {emekli_muktesebat_kademe} {gorunen_emekli_muktesebat_kademe} || __Ek Gösterge__:  {kazanilmis_hak_ekgosterge} || __Terfi Tarihi__:  {em_sonraki_terfi_tarihi}

"""

class PersonelAtama(CrudView):
    """Personel Atama İş Akışı
    Personel atama işlemlerinin gerçekleştiği iş akışıdır.

    Personel atama iş akışı aşağıdaki adımlardan oluşur.

    Kadro Durumunu Kontrol Et:
    Açık kadroların olup olmadığını kontrol eder.

    Eksik Bilgileri Kontrol Et:
    Personelin eksik bilgileri olup olmadığını kontrol eder.

    Eksik Bilgi Form:
    Personele ait eksik bilgiler düzenlenir.

    Eksik Bilgi Kaydet:
    Personele ait eksik bilgiler kaydedilir.

    Atama Durumunu Kontrol Et:
    Personele daha önceden atama yapılıp yapılmadığını kontrol eder.

    Kadro Bilgileri Form:
    Personelin atama bilgileri doldurulur.

    Kadro Bilgileri Göster:
    Personelin kişi bilgilerini ve atama bilgilerini gösterir.

    Atama Kaydet:
    Personel atama bilgileri ve hizmet kayıtları bilgileri kaydedilir.

    Aatama Göster:
    Personelin atama ve kişi bilgileri gösterilir.

    Atama İptal:
    Atama işleminin iptal edildiğine dair bilgi mesajı ekrana basılır.

    Sonuç Bilgisi Göster:
    Personelin bilgilerinin  hitap bilgileri ile  eşlenip eşlenmediğinin sonucu ekrana basar.

    Hitap Bilgilerini Getir:
    Personelin hitap bilgilerini getirir.

    """

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'personel_id' not in self.current.task_data:
            self.current.task_data["personel_id"] = self.current.input["id"]
        p = Personel.objects.get(self.current.task_data['personel_id'])
        self.form_elements = {p: ['kurum_sicil_no_int', 'personel_turu', 'aday_memur',
                             'hizmet_sinifi', 'emekli_sicil_no', 'emekli_giris_tarihi',
                             'statu', 'brans', 'kazanilmis_hak_derece',
                             'kazanilmis_hak_kademe', 'unvan',
                             'gorev_ayligi_derece', 'gorev_ayligi_kademe','gorev_ayligi_ekgosterge',
                             'emekli_muktesebat_ekgosterge','emekli_muktesebat_derece',
                             'kazanilmis_hak_ekgosterge','emekli_muktesebat_kademe',
                             'kh_sonraki_terfi_tarihi', 'ga_sonraki_terfi_tarihi',
                             'em_sonraki_terfi_tarihi', 'mecburi_hizmet_suresi'],
                         p.atama: ['goreve_baslama_tarihi', 'ibraz_tarihi', 'atama_aciklama',
                                   'nereden'],
                         p.kadro: ['kadro_no']}

    def yeni_personel_atama_kontrol(self):
        p = Personel.objects.get(self.current.task_data['personel_id'])
        self.current.task_data['yeni_personel'] = False
        if not p.atama.key:
            self.current.task_data['yeni_personel'] = True

    def guncel_bilgileri_goruntule(self):

        p = Personel.objects.get(self.current.task_data['personel_id'])
        self.output['object'] = {
            "GENEL BİLGİLER:": personel_bilgileri.format(
                kurum_sicil_no_int=p.kurum_sicil_no_int,
                personel_turu=p.get_personel_turu_display(),
                aday_memur= 'Aday' if p.aday_memur else 'Değil',
                hizmet_sinifi=p.get_hizmet_sinifi_display(),
                emekli_sicil_no=p.emekli_sicil_no,
                emekli_giris_tarihi=p.emekli_giris_tarihi,
                statu=p.get_statu_display(),
                brans=p.brans,
                kurumda_ise_baslama_tarihi=p.goreve_baslama_tarihi if p.goreve_baslama_tarihi is not None else "",
                kurum_durum=Atama.personel_ilk_atama(p).durum.__unicode__() if p.atama.key else ""),
            "ÇALIŞTIĞI BİRİMDE İŞE BAŞLAMA:": calistigi_birim.format(
                goreve_baslama_tarihi=p.atama.goreve_baslama_tarihi if p.atama.goreve_baslama_tarihi is not None else "",
                ibraz_tarihi=p.atama.ibraz_tarihi if p.atama.ibraz_tarihi is not None else "",
                durum=p.atama.durum.__unicode__(),
                atama_aciklama=p.atama.atama_aciklama if p.atama.atama_aciklama is not None else "",
                nereden=p.atama.get_nereden_display() if p.atama.nereden else "",
                birim=p.birim.name if p.birim else ""),
            "KADRO UNVAN BİLGİLERİ:": kadro_unvan.format(
                kadro_no=p.kadro.kadro_no,
                kadro_derece_tarihi=p.atama.goreve_baslama_tarihi if p.atama.goreve_baslama_tarihi is not None else "",
                unvan=p.get_unvan_display(),
                unvan_tarihi=p.atama.goreve_baslama_tarihi if p.atama.goreve_baslama_tarihi is not None else "",
                kadro=p.kadro.get_unvan_display(),
                kadro_tarihi=p.atama.goreve_baslama_tarihi if p.atama.goreve_baslama_tarihi is not None else ""),
            "KADRO DERECE BİLGİLERİ:": kadro_derece.format(
                gorev_ayligi_derece=p.gorev_ayligi_derece if p.gorev_ayligi_derece else '-',
                gorev_ayligi_kademe=p.gorev_ayligi_kademe if p.gorev_ayligi_kademe else '-',
                gorunen_gorev_ayligi_kademe= p.gorunen_gorev_ayligi_kademe if p.gorunen_gorev_ayligi_kademe else '-',
                gorev_ayligi_ekgosterge=p.gorev_ayligi_ekgosterge if p.gorev_ayligi_ekgosterge else '-',
                ga_sonraki_terfi_tarihi=p.ga_sonraki_terfi_tarihi if p.ga_sonraki_terfi_tarihi is not None else "",
                kazanilmis_hak_derece=p.kazanilmis_hak_derece if p.kazanilmis_hak_derece else '-',
                kazanilmis_hak_kademe=p.kazanilmis_hak_kademe if p.kazanilmis_hak_kademe else '-',
                gorunen_kazanilmis_hak_kademe = p.gorunen_kazanilmis_hak_kademe if p.gorunen_kazanilmis_hak_kademe else '-',
                kazanilmis_hak_ekgosterge=p.kazanilmis_hak_ekgosterge if p.kazanilmis_hak_ekgosterge else '-',
                kh_sonraki_terfi_tarihi=p.kh_sonraki_terfi_tarihi if p.kh_sonraki_terfi_tarihi is not None else "",
                emekli_muktesebat_derece=p.emekli_muktesebat_derece if p.emekli_muktesebat_derece else '-',
                emekli_muktesebat_kademe=p.emekli_muktesebat_kademe if p.emekli_muktesebat_kademe else '-',
                gorunen_emekli_muktesebat_kademe = p.gorunen_emekli_muktesebat_kademe if p.gorunen_emekli_muktesebat_kademe else '-',
                emekli_muktesebat_ekgosterge=p.emekli_muktesebat_ekgosterge if p.emekli_muktesebat_ekgosterge else '-',
                em_sonraki_terfi_tarihi = p.em_sonraki_terfi_tarihi if p.em_sonraki_terfi_tarihi is not None else "",
            )}

        form = JsonForm(title=_(u"Personel Genel Bilgileri"))
        form.atama_yap = fields.Button(__(u"Atama Yap"), cmd="atama_yap")
        form.duzenle = fields.Button(__(u"Düzenle"), cmd="duzenle")
        form.gecmis_atamalarim = fields.Button(__(u"Atama Listesi"),
                                               cmd="atama_listesi")
        self.form_out(form)

    def guncel_bilgileri_duzenle(self):


        p = Personel.objects.get(self.current.task_data['personel_id'])
        form = PersonelBilgiForm(current=self.current)
        for model, attrs in self.form_elements.items():
            for attr in attrs:
                setattr(form, attr, getattr(model, attr))

        form.kurumda_ise_baslama_tarihi = p.goreve_baslama_tarihi
        form.kadro_unvan = p.kadro.unvan
        form.kadro_derece_tarihi = form.unvan_tarihi = form.kadro_tarihi = form.goreve_baslama_tarihi
        self.form_out(form)

    def degisiklikleri_kaydet(self):

        p = Personel.objects.get(self.current.task_data['personel_id'])
        if self.input['form']['kurumda_ise_baslama_tarihi'] != p.goreve_baslama_tarihi:
            p.goreve_baslama_tarihi = self.input['form']['kurumda_ise_baslama_tarihi']
        if self.input['form']['kadro_unvan'] != p.kadro.unvan:
            p.kadro.unvan = self.input['form']['kadro_unvan']

        p.kadro.blocking_save()
        p.atama.blocking_save()
        p.blocking_save()

        for model, attrs in self.form_elements.items():
            model.reload()
            for attr in attrs:
                if getattr(model, attr) != self.input['form'][attr]:
                    setattr(model, attr, self.input['form'][attr])
            model.blocking_save()


    def atamalari_goruntule(self):

        p = Personel.objects.get(self.current.task_data['personel_id'])
        form = AtamalarForm(current=self.current)

        for atama in sorted(p.AtamaBilgileri, key=lambda a: a.atama_tarihi, reverse=True):
            form.AtamaListesi(atama_bilgisi=atama.atama_bilgisi,
                              atama_tarihi=atama.atama_tarihi,
                              hitap_sebep_no=atama.hitap_sebep_no)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_selection"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def kadro_durumunu_kontrol_et(self):
        """
        Açık kadroların olup olmadığını kontrol eder.

        """
        if not prepare_choices_for_model(Kadro, durum=2):
            self.current.task_data['kadro_bos'] = False
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'Personel Atama Başarısız'),
                "msg": _(u"Kadrolar dolu olduğu için atama yapılamaz.")
            }
        else:
            self.current.task_data['kadro_bos'] = True

    def eksik_bilgileri_kontrol_et(self):
        """
        Personelin eksik bilgileri olup olmadığını kontrol eder.

        """
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        self.current.task_data['personel'] = personel.clean_value()
        if personel.kurum_sicil_no_int:
            self.current.task_data['eksik_bilgi_yok'] = True
        else:
            self.current.task_data['eksik_bilgi_yok'] = False

    def eksik_bilgi_form(self):
        """
        Personele ait eksik bilgiler düzenlenir.

        """
        _form = EksikBilgiForm(current=self.current)
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        durum = [(m.key, m.__unicode__()) for m in HitapSebep.objects.filter(nevi=1)[0:10]]
        _form.kurum_sicil_no_int = fields.Integer(_(u"Kurum Sicil No"),
                                                  default=personel.kurum_sicil_no_int)
        _form.personel_turu = fields.Integer(_(u"Personel Tipi"), choices="personel_turu",
                                             default=personel.personel_turu)
        _form.unvan = fields.Integer(_(u"Personel Unvan"), choices="unvan_kod", required=False,
                                     default=personel.unvan)
        _form.emekli_sicil_no = fields.String(_(u"Emekli Sicil No"),
                                              default=personel.emekli_sicil_no)
        _form.hizmet_sinifi = fields.Integer(_(u"Hizmet Sınıfı"), choices="hizmet_sinifi",
                                            default=personel.hizmet_sinifi)
        _form.statu = fields.Integer(_(u"Statü"), choices="personel_statu", default=personel.statu)
        _form.brans = fields.String(_(u"Branş"), default=personel.brans)
        _form.gorev_suresi_baslama = fields.Date(_(u"Görev Süresi Başlama"),
                                                 default=str(personel.gorev_suresi_baslama))
        _form.gorev_suresi_bitis = fields.Date(_(u"Görev Süresi Bitiş"),
                                               default=str(personel.gorev_suresi_bitis))
        _form.goreve_baslama_tarihi = fields.Date(_(u"Göreve Başlama Tarihi"),
                                                  default=str(personel.goreve_baslama_tarihi))
        # TODO: ulakbüs yavaşladığından dolayı choices slice edildi, typeahead olacak.
        _form.set_choices_of('baslama_sebep', choices=durum)
        # Date formatında mı olacak? yoksa 2 yıl 3 ay gibisinden mi?
        _form.mecburi_hizmet_suresi = fields.Date(_(u"Mecburi Hizmet Süresi"),
                                                  default=str(personel.mecburi_hizmet_suresi))
        _form.emekli_giris_tarihi = fields.Date(_(u"Emekliliğe Giriş Tarihi"),
                                                default=str(personel.emekli_giris_tarihi))

        self.form_out(_form)

    def eksik_bilgi_kaydet(self):
        """
        Personele ait eksik bilgiler kaydedilir.

        """
        from datetime import datetime

        def date_time_object(date_string):
            try:
                datetime.strptime(str(date_string), '%Y-%m-%d')
                return True
            except ValueError:
                return False

        personel = Personel.objects.get(self.current.task_data['personel_id'])
        for value in self.current.input['form']:
            if hasattr(personel, value):
                try:
                    if not date_time_object(self.current.input['form'][value]):
                        setattr(personel, value, self.current.input['form'][value])
                    else:
                        date_str = datetime.strptime(self.current.input['form'][value],
                                                     '%Y-%m-%d').strftime("%d.%m.%Y")
                        setattr(personel, value, datetime.strptime(date_str, "%d.%m.%Y"))
                except ValidationError:
                    setattr(personel, value + "_id", str(self.current.input['form'][value]))
            else:
                continue

        personel.blocking_save()

    def kadro_bilgileri_form(self):
        """
        Personelin atama bilgileri doldurulur.

        """
        _form = KadroBilgiForm(current=self.current,
                               title="{ad} {soyad} adlı personelin atama bilgilerini doldurunuz.".format(
                                   **self.current.task_data['personel'])
                               )

        durum = [(m.key, m.__unicode__()) for m in HitapSebep.objects.filter(nevi=1)[0:10]]
        _form.set_choices_of('kadro', choices=prepare_choices_for_model(Kadro, durum=2))
        _form.set_choices_of('durum', choices=durum)
        self.form_out(_form)

    def atama_kaydet(self):
        """
        Personel atama bilgileri ve hizmet kayıtları bilgileri kaydedilir.

        """

        if not prepare_choices_for_model(Kadro, durum=2):
            self.current.task_data['atama_basarili'] = False
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'Personel Atama Başarısız'),
                "msg": _(u"Kadrolar dolu olduğu için atama yapılamaz.")
            }
        else:
            self.current.task_data['atama_basarili'] = True
            atanacak_kadro = Kadro.objects.get(self.current.input['form']['kadro'])
            personel = Personel.objects.get(self.current.task_data['personel_id'])
            atama = Atama(personel = personel)
            try:
                atama.kadro = atanacak_kadro
                atama.ibraz_tarihi = self.current.input['form']['ibraz_tarihi']
                atama.durum = HitapSebep.objects.get(self.current.input['form']['durum'])
                atama.nereden = self.current.input['form']['nereden']
                atama.atama_aciklama = self.current.input['form']['atama_aciklama']
                atama.goreve_baslama_tarihi = self.current.input['form']['goreve_baslama_tarihi']
                atama.goreve_baslama_aciklama = self.current.input['form'][
                    'goreve_baslama_aciklama']
                atama.blocking_save()
                self.current.task_data['atama_bilgileri'] = atama.clean_value()
                personel.atama = atama
                personel.kadro = atanacak_kadro
                personel.AtamaBilgileri(atama_bilgisi = atama.__unicode__(),
                                        atama_tarihi = atama.goreve_baslama_tarihi,
                                        hitap_sebep_no = atama.durum.sebep_no)
                personel.blocking_save()
                hk = HizmetKayitlari(personel=personel)
                hk.baslama_tarihi = date.today()
                hk.kurum_onay_tarihi = self.current.input['form']['kurum_onay_tarihi']
                hk.sync = 1  # TODO: Düzeltilecek, beta boyunca senkronize etmemesi için 1 yapıldı
                hk.blocking_save()
                self.current.task_data['h_k'] = hk.key
            except Exception as e:
                # Herhangi bir hata oluşursa atama silinecek
                atama.delete()
                self.current.output['msgbox'] = {
                    'type': 'warning', "title": _(u'Hata Oluştu'),
                    "msg": _(u'%s') % e.message
                }

    def atama_goster(self):
        """
        Personelin atama ve kişi bilgileri gösterilir.

        """

        _form = JsonForm(current=self.current, title=_(u"Devam Etmek İstediğiniz İşlemi Seçiniz"))
        _form.hitap = fields.Button(_(u"Hitap ile Eşleştir"), cmd="hitap_getir", btn='hitap')
        _form.bitir = fields.Button(_(u"İşlemi Bitir"), cmd="bitir", form_validation=False)
        self.form_out(_form)

    def atama_iptal(self):
        """
        Atama işleminin iptal edildiğine dair bilgi mesajı ekrana basılır.
        """
        self.current.output['msgbox'] = {
            'type': 'error', "title": _(u'Atama İptal Edildi'),
            "msg": _(u'Personel atama işlemi iptal edildi.'),
        }

    def sonuc_bilgisi_goster(self):
        """
        Personelin bilgilerinin  hitap bilgileri ile  eşlenip eşlenmediğinin sonucu ekrana basar.

        """
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
            "msg": _(u'Atama İşlemi başarıyla gerçekleştirildi. ') + hitap_sonuc
        }

    def hitap_bilgi_getir(self):
        """
        Personelin hitap bilgilerini getirir.

        """
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        from ulakbus.services.zato_wrapper import HitapHizmetCetveliSenkronizeEt
        hizmet_cetveli = HitapHizmetCetveliSenkronizeEt(tckn=str(personel.tckn))

        try:
            hizmet_cetveli.zato_request()
            self.current.task_data['hitap_tamam'] = True
        except:
            self.current.task_data['hitap_tamam'] = False


class AtamalarForm(JsonForm):
    tamam = fields.Button(__(u"Tamam"), cmd="iptal")
    class Meta:
        title = _(u"Atamalar")

    class AtamaListesi(ListNode):
        class Meta:
            title = _(u"Atama Listesi")
        atama_bilgisi = fields.String(_(u"Atama Bilgisi"))
        atama_tarihi = fields.Date(_(u"Atama Tarihi"), format="%d.%m.%Y")
        hitap_sebep_no = fields.Integer(_(u"Hitap Sebep No"))

class EksikBilgiForm(JsonForm):
    """
    Personel Atama wf için form olarak kullanılır.

    """

    class Meta:
        title = _(u'Personelin Eksik Bilgileri')
        # help_text = _(u"Atama Öncesi Personelin Eksik Bilgilerini Düzenleyiniz.")

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": _(u"Genel Bilgiler"),
                        "items": ['kurum_sicil_no_int', 'personel_turu', 'unvan',
                                  'hizmet_sinifi', 'statu', 'brans', 'emekli_sicil_no',
                                  'emekli_giris_tarihi'],
                        "collapse": True,
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": _(u"Mecburi Hizmet Süresi"),
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
                                  'baslama_sebep', 'goreve_baslama_tarihi']
                    }
                ]
            }
        ]

    baslama_sebep = fields.Integer(_(u"Başlama Sebep"))
    kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet", style="btn-success")
    iptal = fields.Button(_(u"İptal"), cmd="iptal", form_validation=False)


class KadroBilgiForm(JsonForm):
    """
    Personel Atama wf  için form olarak kullanılır.

    """

    class Meta:
        title = __(u'Atama Bilgileri')

    kadro = fields.String(_(u"Atanacak Kadro Seçiniz"))  # typeahead olacak
    ibraz_tarihi = fields.Date(_(u"İbraz Tarihi"))
    durum = fields.String(_(u"Durum"))  # typeahead olacak
    nereden = fields.Integer(_(u"Nereden"),choices = "universiteler",required = False)
    atama_aciklama = fields.Text(_(u"Atama Açıklama"))
    goreve_baslama_tarihi = fields.Date(_(u"Göreve Başlama Tarihi"))
    goreve_baslama_aciklama = fields.String(_(u"Göreve Başlama Açıklama"))
    kurum_onay_tarihi = fields.Date(_(u"Kurum Onay Tarihi"))

    kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet", style="btn-success")
    iptal = fields.Button(_(u"İptal"), cmd="iptal", form_validation=False)


class PersonelBilgiForm(JsonForm):
    """
    Personel Atama wf  için form olarak kullanılır.

    """
    kurum_sicil_no_int = fields.Integer(_(u"Kurum Sicil No"))
    personel_turu = fields.Integer(_(u"Personel Tip"), choices="personel_turu")
    aday_memur = fields.Boolean(_(u"Aday"))
    hizmet_sinifi = fields.Integer(_(u"Hizmet Sınıfı"), choices="hizmet_sinifi")
    emekli_sicil_no = fields.String(_(u"Emekli Sicil No"),default = '12345')
    emekli_giris_tarihi = fields.Date(_(u"Emekli Giriş Tarihi"), index=True, format="%d.%m.%Y")
    statu = fields.Integer(_(u"Statü"), choices="personel_statu")
    brans = fields.String(_(u"Branş"))
    kurumda_ise_baslama_tarihi = fields.Date(_(u"Tarihi"), index=True, format="%d.%m.%Y")
    kurum_durum = fields.String(_(u"Durumu"))
    goreve_baslama_tarihi = fields.Date(_(u"Göreve Başlama Tarihi"))
    ibraz_tarihi = fields.Date(_(u"İbraz Tarihi"))
    durum = fields.String(_(u"Durum"))  # typeahead olacak
    atama_aciklama = fields.Text(_(u"Atama Açıklama"), required=False)
    nereden = fields.Integer(_(u"Nereden"),choices='universiteler',type='typeahead')
    mecburi_hizmet_suresi = fields.Date(_(u"Mecburi Hizmet Süresi"), index=True, format="%d.%m.%Y")
    birim = Unit(_(u"Birim"))
    kadro_no = fields.Integer(_(u"Kadro No"), required=False)
    kadro_derece_tarihi = fields.Date(_(u"Tarihi"))
    unvan = fields.Integer(_(u"Personel Unvan"), index=True, choices="unvan_kod", required=False)
    unvan_tarihi = fields.Date(_(u"Tarihi"))
    kadro_unvan = fields.Integer(_(u"Kadro Unvan"),choices="unvan_kod" )
    kadro_tarihi = fields.Date(_(u"Tarihi"))
    kazanilmis_hak_derece = fields.Integer(_(u"Derece"))
    kazanilmis_hak_kademe = fields.Integer(_(u"Kademe"))
    kazanilmis_hak_ekgosterge = fields.Integer(_(u"Ek Gösterge"))
    gorev_ayligi_derece = fields.Integer(_(u"Derece"))
    gorev_ayligi_kademe = fields.Integer(_(u"Kademe"))
    gorev_ayligi_ekgosterge = fields.Integer(_(u"Ek Gösterge"))
    emekli_muktesebat_derece = fields.Integer(_(u"Derece"))
    emekli_muktesebat_kademe = fields.Integer(_(u"Kademe"))
    emekli_muktesebat_ekgosterge = fields.Integer(_(u"Ek Gösterge"))
    kh_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")
    ga_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")
    em_sonraki_terfi_tarihi = fields.Date(_(u"Terfi Tarihi"),
                                          format="%d.%m.%Y")

    kaydet = fields.Button(__(u"Kaydet"), cmd="kaydet")
    iptal = fields.Button(__(u"İptal"), cmd="iptal",form_validation = False)

    class Meta:
        title = __(u'Personel Bilgileri')
        readonly = True

        grouping = [
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": __(u"GENEL BİLGİLER"),
                        "items": ['kurum_sicil_no_int', 'personel_turu',
                                  'aday_memur', 'hizmet_sinifi', 'emekli_sicil_no',
                                  'emekli_giris_tarihi', 'statu', 'brans'
                                  ],
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": __(u"KURUMDA İŞE BAŞLAMA"),
                        "items": ['kurumda_ise_baslama_tarihi', 'kurum_durum',
                                  ],
                    }
                ]
            },
            {
                "layout": "6",
                "groups": [
                    {
                        "group_title": __(u"ÇALIŞTIĞI BİRİMDE İŞE BAŞLAMA"),
                        "items": ['goreve_baslama_tarihi', 'ibraz_tarihi',
                                  'durum', 'atama_aciklama', 'nereden','mecburi_hizmet_suresi'],

                    }
                ]
            },
            {
                "layout": "12",
                "groups": [
                    {
                        "group_title": __(u"BİRİM"),
                        "items": ['birim'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"KADRO DERECE"),
                        "items": ['kadro_no', 'kadro_derece_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"ÜNVAN"),
                        "items": ['unvan', 'unvan_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"KADRO"),
                        "items": ['kadro_unvan', 'kadro_tarihi'],
                    },
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"GÖREV AYLIĞI"),
                        "items": ['gorev_ayligi_derece', 'gorev_ayligi_kademe',
                                  'gorev_ayligi_ekgosterge', 'ga_sonraki_terfi_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"K. HAK AYLIĞI"),
                        "items": ['kazanilmis_hak_derece', 'kazanilmis_hak_kademe',
                                  'kazanilmis_hak_ekgosterge', 'kh_sonraki_terfi_tarihi'],
                    }
                ]
            },
            {
                "layout": "4",
                "groups": [
                    {
                        "group_title": __(u"E. MÜKTESEBİ"),
                        "items": ['emekli_muktesebat_derece', 'emekli_muktesebat_kademe',
                                  'emekli_muktesebat_ekgosterge', 'em_sonraki_terfi_tarihi'],
                    },
                ]
            }

        ]