# -*-  coding: utf-8 -*-
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, OncekiEgitimBilgisi


class YerlestirmeBilgisiForm(forms.JsonForm):
    class Meta:
        include = ["giris_puan_turu", "giris_puani"]

    ileri_buton = fields.Button(gettext_lazy(u"İleri"), cmd="save")


class YerlestirmeBilgisi(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def yerlestirme_bilgisi_form(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci, durum=1)
        self.form_out(YerlestirmeBilgisiForm(ogrenci_program, current=self.current))


class OncekiEgitimBilgileriForm(forms.JsonForm):
    class Meta:
        include = ["okul_adi", "diploma_notu", "mezuniyet_yili"]

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")


class OncekiEgitimBilgileri(CrudView):
    class Meta:
        model = "OncekiEgitimBilgisi"

    def onceki_egitim_bilgileri(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        onceki_egitim_bilgisi = OncekiEgitimBilgisi.objects.filter(ogrenci=ogrenci)
        self.form_out(OncekiEgitimBilgileriForm(onceki_egitim_bilgisi[0], current=self.current))

    def kaydet(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.set_form_data_to_object()
        self.object.ogrenci = ogrenci
        self.object.save()


class OnKayitForm(forms.JsonForm):
    class Meta:
        title = gettext_lazy(u"Kişisel Bilgiler")
        include = ['kan_grubu', 'baba_aylik_kazanc', 'baba_ogrenim_durumu', 'baba_meslek',
                   'anne_ogrenim_durumu', 'anne_meslek', 'anne_aylik_kazanc', 'masraf_sponsor',
                   'emeklilik_durumu', 'kiz_kardes_sayisi', 'erkek_kardes_sayisi',
                   'ogrenim_goren_kardes_sayisi', 'burs_kredi_no', 'aile_tel', 'aile_gsm',
                   'aile_adres', 'ozur_durumu', 'ozur_oran']

    kaydet_buton = fields.Button(gettext_lazy(u"Kaydet"), cmd="kaydet")


class OnKayit(CrudView):
    class Meta:
        model = "Ogrenci"

    def on_kayit_form(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.form_out(OnKayitForm(ogrenci, current=self.current))


class BelgeForm(forms.JsonForm):
    class Meta:
        include = ["Belgeler"]

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")
    onayla = fields.Button(gettext_lazy(u"Ön Kayıt Onayla"), cmd="onayla")


class KayitBelgeler(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def belge_form(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        self.form_out(BelgeForm(ogrenci_program, current=self.current))

    def onayla(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci, durum=1)
        ogrenci_program.durum = 2
        ogrenci_program.save()
