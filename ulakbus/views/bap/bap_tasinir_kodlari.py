# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPFirma
from ulakbus.models import BAPProje

from pyoko import ListNode
from ulakbus.models import BAPButcePlani
from ulakbus.models import BAPSatinAlma
from ulakbus.models import User
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __

from datetime import datetime
from ulakbus.settings import DATE_DEFAULT_FORMAT


class ButceKalemleriForm(JsonForm):
    class Meta:
        inline_edit = ['tasinir_kodu']
        always_blank = False

    class ButceKalemList(ListNode):
        class Meta:
            title = _(u"Bütçe Kalemleri")
        kod_adi = fields.String(_(u"Kod Adı"))
        ad = fields.String(_(u"Ad"))
        muhasebe_kod_genel = fields.Integer(_(u"Öğretim Üyesinin Seçtiği Muhasebe Kodu"),
                                            choices='bap_ogretim_uyesi_gider_kodlari')
        muhasebe_kod = fields.String(_(u"Muhasebe Kodu"),
                                     choices='analitik_butce_dorduncu_duzey_gider_kodlari')
        tasinir_kodu = fields.String(_(u"Taşınır Kodu"), choices='tasinir_kodlari')
        key = fields.String("Key", hidden=True)

    iptal = fields.Button(_(u"Daha Sonra Devam Et"), cmd='daha_sonra_devam_et')
    kaydet = fields.Button(_(u"Kaydet ve Listele"), cmd='kaydet')


class ButceKalemleriFormRO(ButceKalemleriForm):
    class Meta:
        inline_edit = []
        always_blank = False

    ButceKalemList = ButceKalemleriForm.ButceKalemList

    iptal = fields.Button(_(u"Listeye Dön"), cmd='geri')
    kaydet = fields.Button(_(u"Bitir"), cmd='bitir')


class TekFirmaSecForm(JsonForm):
    class Meta:
        title = _(u"Tek Firma Seç")

    firma = BAPFirma()
    daha_sonra_sec = fields.Button(_(u"Daha Sonra Seç"), cmd='daha_sonra_sec',
                                   form_validation=False)
    ileri = fields.Button(_(u"İleri"), cmd='ileri')


class TekFirmaSatinAlmaBilgiGirForm(JsonForm):
    class Meta:
        title = _(u"Satın Alma Bilgileri")

    ad = fields.String(__(u"Satın Alma Duyuru Adı"))
    aciklama = fields.Text(__(u"Açıklama"))
    ileri = fields.Button(_(u"İleri"))


class SatinAlmaIlanBilgiForm(JsonForm):
    class Meta:
        title = _(u"Satın Alma Bilgileri")

    ad = fields.String(__(u"Satın Alma Duyuru Adı"))
    aciklama = fields.Text(__(u"Açıklama"))
    teklife_acilma_tarihi = fields.DateTime(u"Yayınlanma Tarihi")
    teklife_kapanma_tarihi = fields.DateTime(u"Son Teklif Tarihi")
    ileri = fields.Button(_(u"İleri"))


class BAPTasinirKodlari(CrudView):
    def butce_kalemleri_goruntule(self):
        butce_kalemleri = self.current.task_data.get('secilen_butce_planlari')
        form = ButceKalemleriForm(current=self.current, title=_(u"Taşınır Kodları"))
        for bki in butce_kalemleri:
            bk = BAPButcePlani.objects.get(bki)
            form.ButceKalemList(
                kod_adi=bk.kod_adi,
                ad=bk.ad,
                muhasebe_kod_genel=bk.muhasebe_kod_genel,
                muhasebe_kod=bk.muhasebe_kod,
                tasinir_kodu=bk.tasinir_kodu,
                key=bki
            )
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)

    def tasinir_kod_kaydet(self):
        butce_kalemleri = self.input['form']['ButceKalemList']
        for bk in butce_kalemleri:
            butce_plani = BAPButcePlani.objects.get(bk['key'])
            if butce_plani.tasinir_kodu != bk['tasinir_kodu']:
                butce_plani.tasinir_kodu = bk['tasinir_kodu']
                butce_plani.blocking_save()

    def mesaj_goster(self):
        self.current.task_data['ButceKalemleriFormRO'] = self.current.task_data[
            'ButceKalemleriForm']
        form = ButceKalemleriFormRO(current=self.current, title=_(u"Taşınır Kodları"))
        form.help_text = _(u"Bütçe kalemlerinin taşınır kodlarını aşağıdaki gibi kaydettiniz. "
                           u"Düzenleme yapmak için 'Listeye Dön' işlemi tamamlamak için 'Bitir' "
                           u"butonlarını kullanabilirsiniz.")
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        self.form_out(form)

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

    def satin_alma_tur_kontrol(self):
        if self.current.task_data['satin_alma_turu'] in [1, 2, 3]:
            self.current.task_data['cmd'] = 'tek_firma'
        else:
            self.current.task_data['cmd'] = 'ilan'

    def tek_firma_sec(self):
        form = TekFirmaSecForm(current=self.current)
        self.form_out(form)

    def tek_firma_satin_alma_bilgi_gir(self):
        self.current.task_data['tek_firma'] = self.input['form']['firma_id']
        form = TekFirmaSatinAlmaBilgiGirForm()
        self.form_out(form)

    def teklif_daveti_gonder(self):
        firma = BAPFirma.objects.get(self.current.task_data['tek_firma'])
        satin_alma = BAPSatinAlma(
            ad=self.input['form']['ad'],
            ekleyen=self.current.role.user.personel,
            aciklama=self.input['form']['aciklama'],
            teklif_durum=1,
            ilgili_proje=BAPProje.objects.get(self.current.task_data['bap_proje_id']),
            tek_firma=firma,
            tur=self.current.task_data['satin_alma_turu'],
            sorumlu=self.current.role
        ).blocking_save()
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        for y in firma.Yetkililer:
            y.yetkili.send_notification(
                title=_(u"Proje Hakemlik Daveti Yanıtı"),
                message=_(u"%s adlı satın alma için teklif vermeniz beklenmektedir. Satın alma "
                          u"duyurularından satın almayı bulup teklif verebilirsiniz." %
                          satin_alma.ad),
                typ=1,
                sender=sistem_user
            )

    def davet_basarili(self):
        form = JsonForm(title=_(u"Firma Teklif Daveti Başarılı"))
        form.help_text = _(u"Seçtiğiniz firmaya teklif daveti başarıyla gönderilmiştir.")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def satin_alma_ilan_bilgi(self):
        form = SatinAlmaIlanBilgiForm()
        self.form_out(form)

    def satin_alma_kaydet(self):
        d1 = datetime.strptime(self.input['form']['teklife_acilma_tarihi'], DATE_DEFAULT_FORMAT)
        d2 = datetime.strptime(self.input['form']['teklife_kapanma_tarihi'], DATE_DEFAULT_FORMAT)
        BAPSatinAlma(
            ad=self.input['form']['ad'],
            teklife_acilma_tarihi=datetime(d1.year, d1.month, d1.day, 9, 0, 0, 0),
            teklife_kapanma_tarihi=datetime(d2.year, d2.month, d2.day, 16, 0, 0, 0),
            ekleyen=self.current.role.user.personel,
            aciklama=self.input['form']['aciklama'],
            teklif_durum=1,
            ilgili_proje=BAPProje.objects.get(self.current.task_data['bap_proje_id']),
            tur=self.current.task_data['satin_alma_turu'],
            duyuruda=True,
            sorumlu=self.current.role
        ).blocking_save()

    def satin_alma_duyuru_basari(self):
        form = JsonForm(title=_(u"İlan Başarılı"))
        form.help_text = _(u"Satın alma duyurusu başarılı!")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)
