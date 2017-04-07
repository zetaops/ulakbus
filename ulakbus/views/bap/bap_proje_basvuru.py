# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProjeTurleri, BAPProje, Room, Demirbas, Personel, AkademikFaaliyet
from ulakbus.lib.view_helpers import prepare_choices_for_model
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from pyoko import ListNode
import datetime


class ProjeTurForm(JsonForm):
    class Meta:
        title = _(u'Proje Türü Seçiniz')

    tur = fields.String(_(u"Proje Türleri"))
    sec = fields.Button(_(u"Seç"), cmd="kaydet_ve_kontrol")


class GerekliBelgeForm(JsonForm):
    class Meta:
        title = _(u"Seçilen Proje Türü İçin Gerekli Belge ve Formlar")

    class BelgeForm(ListNode):
        class Meta:
            title = _(u"Gerekli Belge ve Formlar")
        ad = fields.String(_(u"Belge Adı"), readonly=True)
        gereklilik = fields.String(_(u"Gereklilik Durumu"), readonly=True)


    iptal = fields.Button(_(u"İptal"), cmd='iptal')
    belgelerim_hazir = fields.Button(_(u"Belgelerim Hazır"), cmd='genel')


class GenelBilgiGirForm(JsonForm):
    class Meta:
        include = ['ad', 'sure', 'anahtar_kelimeler', 'teklif_edilen_baslama_tarihi',
                   'teklif_edilen_butce']
        title = _(u"Proje Genel Bilgileri")

    detay_gir = fields.Button(_(u"Proje Detay Bilgileri"))


class ArastirmaOlanaklariForm(JsonForm):
    class Meta:
        title = _(u"Araştırma Olanakları Ekle")
        help_text = _(u"Üniversite/fakülte envanterinde mevcut olan ve önerilen proje ile ilgili "
                      u"kullanma olanağına sahip olduğunuz personel, yer, teçhizat (marka ve model "
                      u"belirtilerek) vs. hakkında ayrıntılı bilgi verilmelidir.")

    class Olanak(ListNode):
        class Meta:
            title = _(u"Olanaklar")
        ad = fields.String(_(u"Adı"), readonly=True)
        tur = fields.String(_(u"Türü"), readonly=True)

    lab_ekle = fields.Button(_(u"Laboratuvar Ekle"), cmd='lab')
    demirbas_ekle = fields.Button(_(u"Demirbas Ekle"), cmd='demirbas')
    personel_ekle = fields.Button(_(u"Personel Ekle"), cmd='personel')
    ileri = fields.Button(_(u"İleri"), cmd='ilerle')


class LabEkleForm(JsonForm):
    class Meta:
        title = _(u"Laboratuvar Seç")

    lab = fields.String(_(u"Laboratuvar"))
    lab_ekle = fields.Button(_(u"Ekle"))


class DemirbasEkleForm(JsonForm):
    class Meta:
        title = _(u"Demirbaş Seç")

    demirbas = fields.String(_(u"Demirbaş"))
    demirbas_ekle = fields.Button(_(u"Ekle"))


class PersonelEkleForm(JsonForm):
    class Meta:
        title = _(u"Personel Seç")

    personel = fields.String(_(u"Personel"))
    personel_ekle = fields.Button(_(u"Ekle"))


class ProjeCalisanlariForm(JsonForm):
    class Meta:
        title = _(u"Çalışan Ekle")

    class Calisan(ListNode):
        class Meta:
            title = _(u"Çalışanlar")
        ad = fields.String(_(u"Adı"), readonly=True)
        soyad = fields.String(_(u"Soyad"), readonly=True)
        nitelik = fields.String(_(u"Nitelik"), readonly=True)
        calismaya_katkisi = fields.String(_(u"Çalışmaya Katkısı"), readonly=True)

    ileri = fields.Button(_(u"İleri"), cmd='ileri')


class UniversiteDisiUzmanForm(JsonForm):
    class Meta:
        title = _(u"Üniversite Dışı Uzman Ekle")

    class Uzman(ListNode):
        class Meta:
            title = _(u"Uzmanlar")

        ad = fields.String(_(u"Ad"), readonly=True)
        soyad = fields.String(_(u"Soyad"), readonly=True)
        unvan = fields.String(_(u"Unvan"), readonly=True)
        kurum = fields.String(_(u"Kurum"), readonly=True)
        tel = fields.String(_(u"Telefon"), readonly=True)
        faks = fields.String(_(u"Faks"), readonly=True)
        eposta = fields.String(_(u"E-posta"), readonly=True)

    ileri = fields.Button(_(u"İleri"))


class UniversiteDisiDestekForm(JsonForm):
    class Meta:
        title = _(u"Üniversite Dışı Destek Ekle")

    class Destek(ListNode):
        class Meta:
            title = _(u"Destekler")

        kurulus = fields.String(_(u"Destekleyen Kurulus"), readonly=True)
        tur = fields.String(_(u"Destek Türü"), readonly=True)
        destek_miktari = fields.String(_(u"Destek Miktarı"), readonly=True)
        verildigi_tarih = fields.Date(_(u"Verildiği Tarih"), readonly=True)
        sure = fields.Integer(_(u"Süresi(Ay Cinsinden)"), readonly=True)
        destek_belgesi = fields.String(_(u"Destek Belgesi"), readonly=True)

    ileri = fields.Button(_(u"İleri"))


class YurutucuTecrubesiForm(JsonForm):
    class Meta:
        title = _(u"Yürütücü Tecrübesi")

    class AkademikFaaliyet(ListNode):
        ad = fields.String(_(u'Ad'), readonly=True)
        baslama = fields.Date(_(u'Başlama'), readonly=True)
        bitis = fields.Date(_(u'Bitiş'), readonly=True)
        durum = fields.Integer(_(u'Durum'), readonly=True)

    ileri = fields.Button(_(u"İleri"), cmd='ileri')
    ekle = fields.Button(_(u"Ekle"), cmd='ekle')


class YurutucuProjeForm(JsonForm):
    class Meta:
        title = _(u"Yürütücünün Halihazırdaki Projeleri")

    class Proje(ListNode):
        ad = fields.String(_(u'Ad'), readonly=True)
        kurum = fields.String(_(u'Hibe Veren Kurum'), readonly=True)
        miktar = fields.Float(_(u'Hibe Miktarı'), readonly=True)

    ileri = fields.Button(_(u"İleri"), cmd='ileri')


class ProjeDetayForm(JsonForm):
    class Meta:
        include = ['konu_ve_kapsam', 'literatur_ozeti', 'ozgun_deger',
                   'hedef_ve_amac', 'yontem', 'basari_olcutleri', 'b_plani']
        title = _(u"Proje Detayları")

    arastirma_olanaklari = fields.Button(_(u"Araştırma Olanakları"))


class ProjeBasvuru(CrudView):
    class Meta:
        model = "BAPProje"

    def proje_tur_sec(self):
        form = ProjeTurForm()
        form.set_choices_of('tur', prepare_choices_for_model(BAPProjeTurleri))
        self.form_out(form)

    def gerekli_belge_form(self):
        tur_id = self.input['form']['tur']
        tur = BAPProjeTurleri.objects.get(tur_id)
        form = GerekliBelgeForm()
        self.current.task_data['hedef_proje'] = {}
        self.current.task_data['hedef_proje']['tur_id'] = tur_id

        for belge in tur.Belgeler:
            if belge.gereklilik:
                form.BelgeForm(ad=belge.ad, gereklilik=_(u"Gerekli"))

        for proje_form in tur.Formlar:
            if proje_form.gereklilik:
                form.BelgeForm(ad=proje_form.proje_formu.ad, gereklilik=_(u"Gerekli"))

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def proje_genel_bilgilerini_gir(self):
        self.form_out(GenelBilgiGirForm(self.object, current=self.current))

    def proje_detay_gir(self):
        if 'detay_gir' in self.input['form'] and \
                self.input['form']['detay_gir'] == 1:
            for k, v in self.input['form'].items():
                self.current.task_data['hedef_proje'][k] = v
        self.form_out(ProjeDetayForm(self.object, current=self.current))

    def arastirma_olanagi_ekle(self):
        if 'arastirma_olanaklari' in self.input['form'] and \
                self.input['form']['arastirma_olanaklari'] == 1:
            for k, v in self.input['form'].items():
                self.current.task_data['hedef_proje'][k] = v
            self.current.task_data['hedef_proje']['arastirma_olanaklari'] = []
        form = ArastirmaOlanaklariForm()
        for olanak in self.current.task_data['hedef_proje']['arastirma_olanaklari']:
            o = olanak.items()[0]
            if o[0] == 'lab':
                ad = Room.objects.get(o[1]).__unicode__()
                tur = _(u"Laboratuvar")
            elif o[0] == 'demirbas':
                ad = Demirbas.objects.get(o[1]).__unicode__()
                tur = _(u"Demirbaş")
            else:
                ad = Personel.objects.get(o[1]).__unicode__()
                tur = _(u"Personel")
            form.Olanak(ad=ad, tur=tur)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def lab_ekle(self):
        form = LabEkleForm()
        form.set_choices_of('lab', prepare_choices_for_model(Room))
        self.form_out(form)

    def demirbas_ekle(self):
        form = DemirbasEkleForm()
        form.set_choices_of('demirbas', prepare_choices_for_model(Demirbas))
        self.form_out(form)

    def personel_ekle(self):
        form = PersonelEkleForm()
        form.set_choices_of('personel', prepare_choices_for_model(Personel))
        self.form_out(form)

    def olanak_kaydet(self):
        if 'lab' in self.input['form']:
            olanak = {'lab': self.input['form']['lab']}
        elif 'demirbas' in self.input['form']:
            olanak = {'demirbas': self.input['form']['demirbas']}
        else:
            olanak = {'personel': self.input['form']['personel']}

        self.current.task_data['hedef_proje']['arastirma_olanaklari'].append(olanak)

    def calisan_ekle(self):
        form = ProjeCalisanlariForm()
        self.form_out(form)

    def proje_calisan_kaydet(self):
        self.current.task_data['hedef_proje']['proje_calisanlari'] = self.input['form']['Calisan']

    def universite_disi_uzman_ekle(self):
        form = UniversiteDisiUzmanForm()
        self.form_out(form)

    def universite_disi_destek_ekle(self):
        self.current.task_data['hedef_proje']['universite_disi_uzmanlar'] = \
            self.input['form']['Uzman']
        form = UniversiteDisiDestekForm()
        self.form_out(form)

    def yurutucu_tecrubesi(self):
        if 'Destek' in self.input['form']:
            self.current.task_data['hedef_proje']['universite_disi_destek'] = \
                self.input['form']['Destek']
        personel = Personel.objects.get(user_id=self.current.user_id)
        faaliyetler = AkademikFaaliyet.objects.all(personel=personel)

        form = YurutucuTecrubesiForm(current=self.current)

        for faaliyet in faaliyetler:
            form.AkademikFaaliyet(ad=faaliyet.ad, baslama=faaliyet.baslama, bitis=faaliyet.bitis,
                                  durum=faaliyet.durum)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def yurutucu_projeleri(self):
        self.current.task_data['hedef_proje']['tecrube'] = self.input['form']['AkademikFaaliyet']
        personel = Personel.objects.get(user_id=self.current.user_id)
        projeler = BAPProje.objects.all(yurutucu=personel)

        form = YurutucuProjeForm(current=self.current)

        for proje in projeler:
            # todo ad, kurum, miktar
            form.Proje(ad=proje.ad, kurum=None, miktar=None)

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def proje_kaydet(self):
        p = self.current.task_data['hedef_proje']
        del p['form_key']
        del p['detay_gir']
        del p['tecrube']
        p['yurutucu_id'] = Personel.objects.get(user_id=self.current.user_id).key
        proje = BAPProje(**p)
        for olanak in p['arastirma_olanaklari']:
            if 'lab' in olanak:
                proje.ArastirmaOlanaklari(lab_id=olanak['lab'], demirbas=None, personel=None)
            elif 'demirbas' in olanak:
                proje.ArastirmaOlanaklari(lab=None, demirbas_id=olanak['demirbas'], personel=None)
            else:
                proje.ArastirmaOlanaklari(lab=None, demirbas=None, personel_id=olanak['personel'])
        for calisan in p['proje_calisanlari']:
            proje.ProjeCalisanlari(**calisan)
        for destek in p['universite_disi_destek']:
            destek['verildigi_tarih'] = datetime.datetime.strptime(
                destek['verildigi_tarih'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d.%m.%Y")
            proje.UniversiteDisiDestek(**destek)
        for uzman in p['universite_disi_uzmanlar']:
            proje.UniversiteDisiUzmanlar(**uzman)
        self.current.task_data['proje_id'] = proje.blocking_save().key

    def proje_goster(self):
        self.object = BAPProje.objects.get(self.current.task_data['proje_id'])
        self.show()
        form = JsonForm()
        form.onay = fields.Button(_(u"Onaya Gönder"), cmd='onay')
        self.form_out(form)

    def placeholder_method(self):
        form = JsonForm(title=_(u"PlaceHolder"))
        form.button = fields.Button(_(u"Tamam"))
        self.form_out(form)

