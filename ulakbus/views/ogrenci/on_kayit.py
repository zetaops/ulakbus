# -*-  coding: utf-8 -*-
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, OncekiEgitimBilgisi


class OncekiEgitimBilgileriForm(forms.JsonForm):
    class Meta:
        include = ["okul_adi", "diploma_notu", "mezuniyet_yili"]

    ileri_buton = fields.Button(gettext_lazy(u"Kaydet"), cmd="kaydet")


class OncekiEgitimBilgileri(CrudView):
    class Meta:
        model = "OncekiEgitimBilgisi"

    def onceki_egitim_bilgileri(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        onceki_egitim_bilgisi = OncekiEgitimBilgisi.objects.filter(ogrenci=ogrenci)
        self.form_out(OncekiEgitimBilgileriForm(onceki_egitim_bilgisi[0], current=self.current))

    def kaydet(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.object.ogrenci = ogrenci
        self.object.save()


class YerlestirmeBilgisiForm(forms.JsonForm):
    class Meta:
        include = ["giris_puan_turu", "giris_puani"]

    kaydet = fields.Button(gettext_lazy(u"İleri"), cmd="kaydet")


class YerlestirmeBilgisi(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def yerlestirme_bilgisi_form(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci, ogrencilik_statusu=1)
        self.form_out(YerlestirmeBilgisiForm(ogrenci_program, current=self.current))

    def kaydet(self):
        ogrenci = Ogrenci.objects.get(user=self.current.user)
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
        self.object.save()

    def kaydet(self):
        msg = {"title": 'On Kayit Islemi Gonderildi!',
               "body": 'Onay icin ilgili memura gonderildi.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg


class BelgeForm(forms.JsonForm):
    class Meta:
        include = ["Belgeler"]

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")
    onayla = fields.Button(gettext_lazy(u"Ön Kayıt Onayla"), cmd="onayla")


class KayitBelgeler(CrudView):
    class Meta:
        model = "OgrenciProgram"

    def on_kayit_kontrol(self):
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id
        ogrenci = Ogrenci.objects.get(ogrenci_id)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)

        if ogrenci_program.ogrencilik_statusu == 2:
            self.current.task_data['cmd'] = 'kayitli'

    def belge_form(self):
        """
        Öğrencinin kayıtlı olduğu programlar listelenir ve programlardan biri seçilir.

        """

        ogrenci_id = self.current.task_data['ogrenci_id']
        ogrenci = Ogrenci.objects.get(ogrenci_id)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        self.form_out(BelgeForm(ogrenci_program, current=self.current))

    def onayla(self):
        ogrenci_id = self.current.task_data['ogrenci_id']
        ogrenci = Ogrenci.objects.get(ogrenci_id)
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci, ogrencilik_statusu=1)
        ogrenci_program.ogrencilik_statusu = 2
        ogrenci_program.save()

    def on_kayit_tamamlandi(self):

        msg = {"type": 'info',
               "title": 'On Kayit Islemi Gerceklestirildi!',
               "msg": 'Ilgili ogrencinin on kaydini basariyla gerceklestirdiniz.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def kayitli(self):
        msg = {"type": 'info',
               "title": 'Bu Kayit Zaten Var!',
               "msg": 'Ilgili ogrencinin on kaydi daha onceden yapilmistir.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

