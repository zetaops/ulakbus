# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""
    Görevlendirme

    İki tür görevlendirme vardır.
    - Kurum içi görevlendirme
    - Kurum dışı görevlendirme

    Bu iş akışı CrudView nesnesi extend edilerek işletilmektedir.
"""

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import Personel
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri
from zengine.lib.translation import gettext_lazy as __, gettext as _, format_date
from ulakbus.lib.role import AbsRole
from pyoko.exceptions import ObjectDoesNotExist
from dateutil.rrule import MONTHLY, rrule
from datetime import datetime


class YeniGorevlendirmeEkle(JsonForm):
    ekle = fields.Button(__(u"Yeni Ekle"), cmd='tur_sec')


class GorevlendirmeTurSecForm(JsonForm):
    class Meta:
        title = __(u"Görevlendirme Tür Seç")

    gorevlendirme_tur = fields.Integer(__(u"Görevlendirme Tür"), choices="gorev_tipi")
    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="gorevlendirme_tur_kaydet")


class Gorevlendirme(CrudView):
    class Meta:
        model = "Personel"

    def gorev_listesi(self):

        if 'personel_id' not in self.current.task_data:
            personel_id = self.current.input["id"]
            self.current.task_data["personel_id"] = personel_id
        else:
            personel_id = self.current.task_data['personel_id']

        kurum_ici_gorevlendirme_bilgileri = KurumIciGorevlendirmeBilgileri.objects.filter(
            personel_id=personel_id)
        kurum_disi_gorevlendirme_bilgileri = KurumDisiGorevlendirmeBilgileri.objects.filter(
            personel_id=personel_id)

        gorevler = [k for k in kurum_ici_gorevlendirme_bilgileri]
        gorevler += [k for k in kurum_disi_gorevlendirme_bilgileri]

        self.form_out(YeniGorevlendirmeEkle(title=__(u"Görevlendirme Listesi")))

        self.output['objects'] = [[_(u'Görev Tipi'), _(u'Başlama Tarihi'), _(u'Bitiş Tarihi')], ]

        for gorev in gorevler:
            item = {
                "fields": ["%s" % gorev.get_gorev_tipi_display(),
                           "%s" % format_date(gorev.baslama_tarihi) if gorev.baslama_tarihi else '',
                           "%s" % format_date(gorev.bitis_tarihi) if gorev.bitis_tarihi else ''],
                "actions": [{'name': _(u'Sil'), 'cmd': 'sil',
                             'show_as': 'button', 'object_key': 'gorev_key'},
                            {'name': _(u'Düzenle'), 'cmd': 'duzenle',
                             'show_as': 'button', 'object_key': 'gorev_key'}],
                "key": gorev.key
            }
            self.output['objects'].append(item)

        self.output['meta']['allow_search'] = False

    def gorev_duzenle(self):
        gorev_key = self.input['gorev_key']
        try:
            KurumDisiGorevlendirmeBilgileri.objects.get(gorev_key)
            tur = 1
        except ObjectDoesNotExist:
            KurumIciGorevlendirmeBilgileri.objects.get(gorev_key)
            tur = 2

        self.current.task_data['gorevlendirme_tur'] = tur
        self.current.task_data['object_id'] = gorev_key

    def gorev_sil_onay_formu(self):
        gorev_key = self.input['gorev_key']
        try:
            obj = KurumDisiGorevlendirmeBilgileri.objects.get(gorev_key)
            self.Meta.model = 'KurumDisiGorevlendirmeBilgileri'
        except ObjectDoesNotExist:
            obj = KurumIciGorevlendirmeBilgileri.objects.get(gorev_key)
            self.Meta.model = 'KurumIciGorevlendirmeBilgileri'

        self.current.task_data['object_id'] = obj.key

        form = JsonForm(title=_(u"Görev Silme İşlemi"))
        form.help_text = _(

u"""Ad Soyad: **%(ad)s** **%(soyad)s**

Başlama Tarihi: **%(baslama_tarihi)s**

Bitiş Tarihi: **%(bitis_tarihi)s**

Görev Tipi: **%(sure)s**

Bilgilerin bulunduğu görevi silmek istiyor musunuz?"""

        ) % {'ad': obj.personel.ad,
             'soyad': obj.personel.soyad,
             'baslama_tarihi': obj.baslama_tarihi,
             'bitis_tarihi': obj.bitis_tarihi,
             'sure': obj.get_gorev_tipi_display()}
        form.evet = fields.Button(__(u"Evet"), cmd='delete')
        form.hayir = fields.Button(__(u"Hayır"))
        self.form_out(form)

    def gorevlendirme_tur_sec(self):
        """
            Görevlendirme tipinin seçildiği formu return eden bir metoddur.
        """

        # Seçili personel id si saklanıyor
        self.form_out(GorevlendirmeTurSecForm())

    def gorevlendirme_tur_kaydet(self):
        # Görevlendirme türü wf nin ilerleyen adımları için task data da saklandı
        self.current.task_data["gorevlendirme_tur"] = self.current.input["form"][
            "gorevlendirme_tur"]


class KurumIciGorevlendirmeForm(JsonForm):
    class Meta:
        exclude = ["gorev_tipi", "personel", ]

        title = __(u"Kurum İçi Görevlendirme")

    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="kaydet")


class KurumIciGorevlendirme(CrudView):
    class Meta:
        model = "KurumIciGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        if 'hata_msg' in self.current.task_data:
            self.current.output['msgbox'] = {"type": "warning",
                                             "title": _(u"Hatalı Tarih Girişi"),
                                             "msg": _(u"%(hata_msg)s") % {
                                                 'hata_msg': self.current.task_data['hata_msg']
                                                }
                                             }
            del self.current.task_data['hata_msg']
        self.form_out(KurumIciGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        self.set_form_data_to_object()
        self.object.gorev_tipi = self.current.task_data['gorevlendirme_tur']
        self.object.personel = Personel.objects.get(self.current.task_data['personel_id'])
        hata_msg = ''

        if form_data['baslama_tarihi'] > form_data['bitis_tarihi']:
            hata_msg = "Başlangıç tarihi, bitiş tarihinden büyük olamaz"

        if hata_msg:
            self.current.task_data['hata_msg'] = hata_msg
            self.current.task_data['hatali'] = 1
        else:
            self.object.blocking_save()
            self.current.task_data['hatali'] = 0
            self.current.task_data["hizmet_cetvel_giris"] = form_data["soyut_rol_id"] in [
                AbsRole.FAKULTE_DEKANI.name, AbsRole.REKTOR.name]
            if 'object_id' in self.current.task_data:
                del self.current.task_data['object_id']


class KurumDisiGorevlendirmeForm(JsonForm):
    class Meta:
        exclude = ["gorev_tipi", "personel", ]

        title = __(u"Kurum Dışı Görevlendirme")

    kaydet = fields.Button(__(u"Kaydet ve Devam Et"), cmd="kaydet")


class KurumDisiGorevlendirme(CrudView):
    class Meta:
        model = "KurumDisiGorevlendirmeBilgileri"

    def gorevlendirme_form(self):
        if 'hata_msg' in self.current.task_data:
            self.current.output['msgbox'] = {"type": "warning",
                                             "title": _(u"Hatalı Tarih Girişi"),
                                             "msg": _(u"%(hata_msg)s") % {
                                                 'hata_msg': self.current.task_data['hata_msg']
                                                }
                                             }
            del self.current.task_data['hata_msg']
            self.set_form_data_to_object()
        self.form_out(KurumDisiGorevlendirmeForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        self.set_form_data_to_object()
        self.object.gorev_tipi = self.current.task_data['gorevlendirme_tur']
        self.object.personel = Personel.objects.get(self.current.task_data['personel_id'])
        hata_msg = ''

        baslangic_tarihi = datetime.strptime(form_data['baslama_tarihi'], "%d.%m.%Y").date()
        bitis_tarihi = datetime.strptime(form_data['bitis_tarihi'], "%d.%m.%Y").date()

        alti_yil_onceki_tarih = baslangic_tarihi.replace(year=baslangic_tarihi.year-6)
        iki_yil_onceki_tarih = baslangic_tarihi.replace(year=baslangic_tarihi.year-2)

        maasli_gorev = KurumDisiGorevlendirmeBilgileri.objects.filter(
            baslama_tarihi__gt=alti_yil_onceki_tarih,
            maas=True)
        maassiz_gorev = KurumDisiGorevlendirmeBilgileri.objects.filter(
            baslama_tarihi__gt=iki_yil_onceki_tarih,
            maas=False)
        sure = rrule(MONTHLY, dtstart=baslangic_tarihi, until=bitis_tarihi).count()

        if baslangic_tarihi > bitis_tarihi:
            hata_msg = "Başlangıç tarihi, bitiş tarihinden büyük olamaz"
        if sure > 3:
            if maasli_gorev:
                hata_msg = "6 yıl içerisinde alınmış maaşlı görev bulunmaktadır. " \
                           "Yeni görev süresi 3 aydan fazla olmamalıdır!"
            elif maassiz_gorev:
                hata_msg = "2 yıl içerisinde alınmış maaşsız görev bulunmaktadır. " \
                           "Yeni görev süresi 3 aydan fazla olmamalıdır!"

        if hata_msg:
            self.current.task_data['hata_msg'] = hata_msg
            self.current.task_data['hatali'] = 1
        else:
            self.object.blocking_save()
            self.current.task_data['hatali'] = 0
            self.current.task_data["hizmet_cetvel_giris"] = form_data["soyut_rol_id"] in [
                AbsRole.FAKULTE_DEKANI.name, AbsRole.REKTOR.name]
            if 'object_id' in self.current.task_data:
                del self.current.task_data['object_id']


class HizmetCetveliForm(JsonForm):
    class Meta:
        exclude = ["tckn", "sync", "personel", "model_key", "order_date"]

        title = __(u"Hizmet Cetveli Form")

    kaydet_buton = fields.Button(__(u"Kaydet"))


class HizmetCetveli(CrudView):
    class Meta:
        model = "HizmetKayitlari"

    def giris_form(self):
        personel = Personel.objects.get(self.current.task_data["personel_id"])

        self.object.kadro_derece = personel.kadro_derece
        self.object.kazanilmis_hak_ayligi_derece = personel.kazanilmis_hak_derece
        self.object.kazanilmis_hak_ayligi_kademe = personel.kazanilmis_hak_kademe
        self.object.kazanilmis_hak_ayligi_ekgosterge = personel.kazanilmis_hak_ekgosterge
        self.object.emekli_derece = personel.emekli_muktesebat_derece
        self.object.emekli_kademe = personel.emekli_muktesebat_kademe
        self.object.emekli_ekgosterge = personel.emekli_muktesebat_ekgosterge

        self.form_out(HizmetCetveliForm(self.object, current=self.current))

    def kaydet(self):
        form_data = self.current.input["form"]
        personel = Personel.objects.get(self.current.task_data["personel_id"])

        self.set_form_data_to_object()
        self.object.personel = personel
        self.object.tckn = personel.tckn

        if "sebep_kod" in form_data:
            self.object.sebep_kod = form_data["sebep_kod"]
        self.object.blocking_save()
