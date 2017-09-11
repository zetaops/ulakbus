# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPIsPaketi
from ulakbus.models import BAPButcePlani
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.settings import DATE_DEFAULT_FORMAT
from collections import OrderedDict


class GenelProjeForm(JsonForm):
    """
    Koordinasyon biriminin projeyi incelerken kategoriler arasında geçiş
    yapabileceği ve inceleme sonrası karar vermesini sağlayan form.

    """

    genel = fields.Button(_(u"Genel"), cmd='genel')
    detay = fields.Button(_(u"Detay"), cmd='olanak')
    butce = fields.Button(_(u"Bütçe"), cmd='butce_plani')
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari')
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani')
    iptal = fields.Button(_(u"Daha Sonra Karar Ver"), cmd='iptal', style="btn-info")
    karar_ver = fields.Button(_(u"Karar Ver"), cmd='karar_ver', style="btn-info")


class DetayProjeForm(JsonForm):
    """
    Projenin araştırma olanakları, üniversite dışı uzmanları gibi detaylarını
    göstermek için kullanılan form.

    """

    olanak = fields.Button(_(u"Araştırma Olanakları"), cmd='olanak')
    dis_uzman = fields.Button(_(u"Dış Uzmanlar"), cmd='dis_uzman')
    dis_destek = fields.Button(_(u"Dış Destekler"), cmd='dis_destek')
    geri = fields.Button(_(u"Geri Dön"), cmd='geri_don')


class IsPlaniAyrintilariForm(JsonForm):
    """
    İş paketlerinin içinde bulunan işlerin ayrıntılı gösterilmesine yarayan form.

    """
    geri = fields.Button(_(u"Geri Dön"))


class BasvuruInceleme(CrudView):
    class Meta:
        model = "BAPProje"

    def __init__(self, current):
        CrudView.__init__(self, current)
        if not self.object.key:
            self.object = self.model_class.objects.get(self.current.task_data.get('bap_proje_id',self.input.pop('object_id', '')))
        self.current.output["meta"]["allow_search"] = False

        # Genel form, bu nesneyi extend eden digerleri tarafindan degistirilebilsin
        # bkz: bap_ogrbasvuru_goruntule.py
        self.genel_form = GenelProjeForm

    def genel_proje_bilgileri_goster(self):
        """
        Proje hakkında genel bilgileri gösterir.

        """

        proje_bilgileri = OrderedDict([
            ('Proje Adı', self.object.ad),
            ('Proje Yürütücüsü', self.object.yurutucu.__unicode__()),
            ('Proje Süresi(Ay)', str(self.object.sure)),
            ('Teklif Edilen Başlama Tarihi',
             self.object.teklif_edilen_baslama_tarihi.strftime(
                 DATE_DEFAULT_FORMAT) if self.object.teklif_edilen_baslama_tarihi else ''),
            ('Teklif Edilen Bütçe', str(self.object.teklif_edilen_butce)),
            ('Anahtar Kelimeler', self.object.anahtar_kelimeler),
            ('Konu ve Kapsam', self.object.konu_ve_kapsam),
            ('Literatür Özeti', self.object.literatur_ozeti),
            ('Özgün Değer', self.object.ozgun_deger),
            ('Hedef ve Amaç', self.object.hedef_ve_amac),
            ('Yöntem', self.object.yontem),
            ('Başarı Ölçütleri', self.object.basari_olcutleri),
            ('B Planı', self.object.b_plani),
        ])
        self.output['object'] = proje_bilgileri
        self.form_out(self.genel_form(title=__('Proje Hakkında')))

    def proje_calisanlari_goster(self):
        """
        Proje Çalışanları listnode'u gösterilir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [[_(u'Ad'), _(u'Soyad'), _(u'Nitelik'), _(u'Çalışmaya Katkısı')]]
        self.form_out(self.genel_form(title = __('Proje Çalışanları')))
        for calisan in self.object.ProjeCalisanlari:
            ad = calisan.ad
            soyad = calisan.soyad
            nitelik = calisan.nitelik
            calismaya_katkisi = calisan.calismaya_katkisi
            list_item = {
                "fields": [ad, soyad, nitelik, calismaya_katkisi],
                "actions": '',
            }
            self.output['objects'].append(list_item)

    def butce_plani_goster(self):
        """
        Projenin bütçe planını gösterir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [
            [_('Muhasebe Kodu'), _(u'Kod Adı'), _(u'Kalem Adı'), _(u'Birim Fiyatı'),
             _(u'Adet'), _('Toplam Fiyat'), _('Gerekçe')]]

        for plan in BAPButcePlani.objects.filter(ilgili_proje=self.object).order_by():
            muhasebe_kodu = plan.muhasebe_kod
            kod_adi = plan.kod_adi
            ad = plan.ad
            birim_fiyat = str(plan.birim_fiyat)
            adet = str(plan.adet)
            toplam_fiyat = str(plan.toplam_fiyat)
            gerekce = plan.gerekce

            list_item = {
                "fields": [muhasebe_kodu, kod_adi, ad, birim_fiyat, adet, toplam_fiyat, gerekce],
                "actions": "",
            }
            self.output['objects'].append(list_item)
        self.form_out(self.genel_form(title=__('Bütçe Planı')))

    def is_plani_goster(self):
        """
        Projenin iş paketlerini gösterir.

        """

        self.current.output["meta"]["allow_actions"] = True
        self.output['objects'] = [[_(u'Paket Adı'), _(u'Başlangıç Tarihi'), _(u'Bitiş Tarihi')]]
        for plan in BAPIsPaketi.objects.filter(proje=self.object).order_by():
            ad = plan.ad
            bas_tarih = plan.baslama_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if plan.baslama_tarihi else ''

            bit_tarih = plan.bitis_tarihi.strftime(DATE_DEFAULT_FORMAT) if plan.bitis_tarihi else ''

            list_item = {
                "fields": [ad, bas_tarih, bit_tarih],
                "actions": [
                    {'name': _(u'Ayrıntı Göster'), 'cmd': 'ayrinti', 'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': plan.key}

            self.output['objects'].append(list_item)
        self.form_out(self.genel_form(title=__('İş Planı')))

    def is_plani_ayrintili_goster(self):
        """
        Projenin iş paketleri içerisinden seçilen o iş paketini
        oluşturan işlerin ayrıntıları gösterilir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [[_(u'İş Adı'), _(u'Başlangıç Tarihi'), _(u'Bitiş Tarihi')]]
        is_paketi = BAPIsPaketi.objects.get(self.current.input['data_key'])
        self.form_out(IsPlaniAyrintilariForm(title='%s İş Planı Ayrıntıları' % is_paketi.ad))
        for bap_is in is_paketi.Isler:
            ayrinti_is = bap_is.isler
            ad = ayrinti_is.ad
            bas_tarih = ayrinti_is.baslama_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if ayrinti_is.baslama_tarihi else ''
            bit_tarih = ayrinti_is.bitis_tarihi.strftime(
                DATE_DEFAULT_FORMAT) if ayrinti_is.bitis_tarihi else ''
            list_item = {
                "fields": [ad, str(bas_tarih), str(bit_tarih)],
                "actions": '',
            }

            self.output['objects'].append(list_item)

    def arastirma_olanaklari_goster(self):
        """
        Projenin araştırma olanakları listnode'u gösterilir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [[_(u'Demirbaş'), _(u'Personel'), _(u'Oda')]]
        self.form_out(DetayProjeForm(title=__('Araştırma Olanakları')))
        for olanak in self.object.ArastirmaOlanaklari:
            demirbas = olanak.demirbas.ad
            personel = olanak.personel.__unicode__() if olanak.personel.key else ''
            oda = olanak.lab.name
            list_item = {
                "fields": [demirbas, personel, oda],
                "actions": '',
            }
            self.output['objects'].append(list_item)

    def universite_disi_uzman_goster(self):
        """
        Projenin üniversite dışı uzman listnode'u gösterilir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [
            [_(u'Ad'), _(u'Soyad'), _(u'Unvan'), _(u'Kurum'), _(u'Tel'), _(u'Faks'), _(u'E-Posta')]]
        self.form_out(DetayProjeForm(title=__('Üniversite Dışı Uzmanlar')))
        for uzman in self.object.UniversiteDisiUzmanlar:
            ad = uzman.ad
            soyad = uzman.soyad
            unvan = uzman.unvan
            kurum = uzman.kurum
            tel = uzman.tel
            faks = uzman.faks
            eposta = uzman.eposta
            list_item = {
                "fields": [ad, soyad, unvan, kurum, tel, faks, eposta],
                "actions": '',
            }
            self.output['objects'].append(list_item)

    def universite_disi_destek_goster(self):
        """
        Projenin üniversite dışı destek listnode'u gösterilir.

        """

        self.current.output["meta"]["allow_actions"] = False
        self.output['objects'] = [
            [_(u'Kuruluş'), _(u'Tür'), _(u'Destek Miktarı'), _(u'Verildiği Tarih'), _(u'Süre'),
             _(u'Destek Belgesi')]]
        self.form_out(DetayProjeForm(title=__('Üniversite Dışı Destekler')))
        for destek in self.object.UniversiteDisiDestek:
            kurulus = destek.kurulus
            tur = destek.tur
            destek_miktari = destek.destek_miktari
            verildigi_tarih = destek.verildigi_tarih.strftime(
                DATE_DEFAULT_FORMAT) if destek.verildigi_tarih else ''
            sure = destek.sure
            destek_belgesi = ''

            list_item = {
                "fields": [kurulus, tur, destek_miktari, verildigi_tarih, sure, destek_belgesi],
                "actions": '',
            }
            self.output['objects'].append(list_item)
