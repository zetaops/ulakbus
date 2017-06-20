# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.views.bap.bap_proje_degerlendirme_goruntule import catalog_to_dict
from pyoko import ListNode
from ulakbus.models import AbstractRole
from ulakbus.models import BAPButcePlani, BAPProje
from ulakbus.models import BAPSatinAlma
from ulakbus.models import Personel
from ulakbus.models import Role
from zengine.forms import JsonForm
from zengine.lib.catalog_data import catalog_data_manager
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.forms import fields
from ulakbus.settings import DATE_DEFAULT_FORMAT, DATETIME_DEFAULT_FORMAT
import datetime


class ButceKalemleriForm(JsonForm):
    """
    Bütçe kalemlerinin gösterildiği formdur.
    """
    class Meta:
        title = __(u"Bütçe Kalemleri")
        inline_edit = ['sec']

    class Kalem(ListNode):
        sec = fields.Boolean(_(u"Seç"), type="checkbox")
        ad = fields.String(_(u"Tanımı/Adı"), readonly=True)
        adet = fields.Integer(_(u"Adet"), readonly=True)
        alim_kalemi_sartnamesi = fields.String(_(u"Alım Kalemi Şartnamesi"), readonly=True)
        genel_sartname = fields.String(_(u"Genel Şartname"), readonly=True)
        butce_plan_key = fields.String(_(u"Key"), hidden=True)

    iptal = fields.Button(_(u"İptal Et ve Proje Listesine Dön"), cmd='iptal')
    satin_alma_listesine_don = fields.Button(_(u"İptal Et ve Satın Alma Listesine Dön"),
                                             cmd='listeye_don')
    tamam = fields.Button(_(u"Tamam"), cmd='tamam')


class SatinAlmaTalebiForm(JsonForm):
    """
    Satın alma talebi alanlarının alındığı, koordinasyon biriminin dolduracağı formdur.
    """
    class Meta:
        title = __(u"Satın Alma Talebi")

    satin_alma_talep_adi = fields.String(u"Satın Alma Başlığı")
    yurutucu = fields.String(u"Proje Yürütücüsü")
    onay_tarih_sayi = fields.String(u"Onay Tarihi/Sayı")
    teklife_acilma_tarihi = fields.DateTime(u"Yayınlanma Tarihi")
    son_teklif_tarihi = fields.DateTime(u"Son Teklif Tarihi")
    ekleyen = fields.String(u"Ekleyen")
    aciklama = fields.Text(u"Açıklama", required=False)
    iptal_satin_alma = fields.Button(_(u"İptal Et ve Satın Alma Listesine Dön"), cmd='listeye_don',
                                     form_validation=False)
    kaydet = fields.Button(_(u"Kaydet"), cmd='kaydet')


class BAPSatinAlmaView(CrudView):
    """
    Koordinasyon biriminin satın alma talebi yapılan projeler üzerinde çalıştırdığı, yapılan satın
    alma taleplerini görüntülediği, uygun bulduklarını satın almaya çıkardığı iş akışıdır.
    """

    def __init__(self, current):
        CrudView.__init__(self, current)
        if self.cmd != 'confirm_deletion' and self.cmd != 'delete' \
                and 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

    def satin_almalari_listele(self):
        """
        Projenin varsa önceki satın almaları listelenir. Satın almalar düzenlenip silinebilir.
        Yoksa yeni satın alma eklenebilir. Yeni satın alma eklenirken mevcut bütçe kalemleri içinden
        koordinasyon birimi kullanıcısının seçtiği bir veya daha fazla bütçe kalemi alınıp satın
        alma oluşturulur.
        """
        self.current.task_data['obj_id'] = self.input.get('object_id') or \
                                           self.current.task_data['obj_id']
        proje = BAPProje.objects.get(self.current.task_data['obj_id'])
        form = JsonForm(title=_(u"Satın Almalar: %s" % proje.__unicode__()))
        form.ekle = fields.Button(_(u"Ekle"), cmd='ekle')
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        satin_almalar = BAPSatinAlma.objects.filter(ilgili_proje=proje)
        self.output['objects'] = [[_(u'Ad'), _(u'Teklife Açılma Tarihi'),
                                   _(u"Teklife Kapanma Tarihi"), _(u"Durum")], ]

        d = catalog_to_dict(catalog_data_manager.get_all('bap_satin_alma_durum'))

        for s in satin_almalar:
            tat = s.teklife_acilma_tarihi.strftime(DATETIME_DEFAULT_FORMAT)
            tkt = s.teklife_kapanma_tarihi.strftime(DATETIME_DEFAULT_FORMAT)
            list_item = {
                "fields": [s.ad, tat, tkt, d[s.teklif_durum]],
                "actions": [
                    {'name': _(u'Düzenle'), 'cmd': 'edit', 'show_as': 'button',
                     'object_key': 'satin_alma'},
                    {'name': _(u'Sil'), 'cmd': 'sil', 'show_as': 'button',
                     'object_key': 'satin_alma'},
                ],
                "key": s.key
            }

            self.output['objects'].append(
                list_item
            )
        self.form_out(form)

    def satin_alma_sil(self):
        """
        Eklenen satın almanın silindiği adımdır. Satın alma silinirken, satın almaya eklenen bütçe
         kalemlerinin durumları da önceki haline getirilir.
        """
        satin_alma = BAPSatinAlma.objects.get(self.input.get('satin_alma'))
        for bk in satin_alma.ButceKalemleri:
            butce_key = bk.butce.key
            butce_plani = BAPButcePlani.objects.get(butce_key)
            butce_plani.satin_alma_durum = 1
            butce_plani.blocking_save()
        satin_alma.blocking_delete()

    def satin_alma_duzenle(self):
        """
        Satın alma ilanının düzenlendiği adımdır. Satın alma duyurusuna çıkacak alanlar düzenlenir.
        """
        self.current.task_data['satin_alma_id'] = self.input.get('satin_alma')
        satin_alma = BAPSatinAlma.objects.get(self.input.get('satin_alma'))
        proje = BAPProje.objects.get(self.current.task_data['obj_id'])
        form = SatinAlmaTalebiForm()
        form.set_choices_of('yurutucu', choices=[(proje.yurutucu().key,
                                                  proje.yurutucu().__unicode__())])
        ar = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi - Koordinasyon Birimi')
        role_list = Role.objects.filter(abstract_role=ar)
        personel_list = [Personel.objects.get(user=rr.user()) for rr in role_list]
        form.set_choices_of('ekleyen', choices=[(p.key, p.__unicode__()) for p in personel_list])
        form.satin_alma_talep_adi = satin_alma.ad
        form.yurutucu = proje.yurutucu().key
        form.onay_tarih_sayi = satin_alma.onay_tarih_sayi
        form.teklife_acilma_tarihi = satin_alma.teklife_acilma_tarihi
        form.son_teklif_tarihi = satin_alma.teklife_kapanma_tarihi
        form.ekleyen = satin_alma.ekleyen().key
        form.aciklama = satin_alma.aciklama

        self.form_out(form)

    def duzenleme_kaydet(self):
        """
        Satın alma düzenlemesinin kaydedildiği adımdır.
        """
        proje = BAPProje.objects.get(self.current.task_data['obj_id'])
        satin_alma = BAPSatinAlma.objects.get(self.current.task_data.pop('satin_alma_id'))
        talep_form = self.current.task_data['SatinAlmaTalebiForm']
        satin_alma.aciklama = talep_form['aciklama']
        satin_alma.ad = talep_form['satin_alma_talep_adi']
        d1 = datetime.datetime.strptime(
            talep_form['teklife_acilma_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.teklife_acilma_tarihi = datetime.datetime(d1.year, d1.month, d1.day, 9, 0, 0, 0)
        d2 = datetime.datetime.strptime(
            talep_form['son_teklif_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.teklife_kapanma_tarihi = datetime.datetime(d2.year, d2.month, d2.day, 16, 0, 0, 0
                                                              )
        satin_alma.onay_tarih_sayi = talep_form['onay_tarih_sayi']
        satin_alma.ekleyen = Personel.objects.get(talep_form['ekleyen'])
        satin_alma.ilgili_proje = proje
        satin_alma.teklif_durum = 1

        satin_alma.blocking_save()

    def butce_kalemleri_sec_goster(self):
        """
        Satın almaya çıkarılacak bütçe kalemlerinin seçildiği adımdır.
        """
        msg = self.current.task_data.pop('uyari_mesaji', None)
        if msg:
            self.current.output['msgbox'] = {
                'type': 'error',
                "title": _(u"Eksik Seçim"),
                "msg": msg}

        butce_planlari = BAPButcePlani.objects.filter(
            ilgili_proje_id=self.current.task_data['obj_id'], satin_alma_durum=2)

        form = ButceKalemleriForm()
        form.help_text = _(u"Satın alma talebi oluşturulacak bütçe kalemleri seçilmelidir.")
        for bp in butce_planlari:
            form.Kalem(
                sec=False,
                ad=bp.ad,
                adet=bp.adet,
                alim_kalemi_sartnamesi="",
                genel_sartname="",
                butce_plan_key=bp.key,
            )

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def secimi_kontrol_et(self):
        """
        Bütçe kalemleri seçilip seçilmediğini kontrol eden adımdır. Eğer hiç bütçe kalemi
        seçilmediyse bütçe kalemi seçilmesine dair bir uyarı ile bütçe kalemi seçimi adımına döner.
         Eğer en az bir bütçe kalemi seçildiyse, satın alma talebi oluşturma adımına devam edilir.
        """
        kalemler = self.input['form']['Kalem']
        for kalem in kalemler:
            if kalem['sec']:
                self.current.task_data['cmd'] = 'gecerli'
                break
        else:
            self.current.task_data['uyari_mesaji'] = _(u"""Satın alma talebi oluşturmak için bütçe
            kalemi seçmediniz. Devam etmek için bütçe kalemi seçilmelidir.""")
            self.current.task_data['cmd'] = 'gecersiz'

    def satin_alma_talebi_olustur(self):
        """
        Satın alma duyurusunda gösterilecek alanların ve satın alma bilgilerinin doldurulduğu
        adımdır.
        """
        obj_id = self.current.task_data['obj_id']
        proje = BAPProje.objects.get(obj_id)
        form = SatinAlmaTalebiForm()
        form.set_choices_of('yurutucu', choices=[(proje.yurutucu().key,
                                                  proje.yurutucu().__unicode__())])
        form.set_default_of('yurutucu', default=proje.yurutucu().key)
        ar = AbstractRole.objects.get(name='Bilimsel Arastirma Projesi - Koordinasyon Birimi')
        role_list = Role.objects.filter(abstract_role=ar)
        personel_list = [Personel.objects.get(user=rr.user()) for rr in role_list]
        form.set_choices_of('ekleyen', choices=[(p.key, p.__unicode__()) for p in personel_list])
        form.set_default_of('ekleyen',
                            default=Personel.objects.get(user_id=self.current.user_id).key)
        form.iptal = fields.Button(_(u"İptal Et ve Proje Listesine Dön"), cmd='iptal',
                                   form_validation=False)
        form.geri = fields.Button(_(u"İptal Et ve Bütçe Kalemlerine Dön"), cmd='geri',
                                  form_validation=False)
        self.form_out(form)

    def satin_alma_talebi_kaydet(self):
        """
        Satın alma talebinin kaydedildiği adımdır.
        """
        proje = BAPProje.objects.get(self.current.task_data['obj_id'])
        satin_alma = BAPSatinAlma()
        kalemler = self.current.task_data['ButceKalemleriForm']['Kalem']
        talep_form = self.current.task_data['SatinAlmaTalebiForm']
        for kalem in kalemler:
            if kalem['sec']:
                butce = BAPButcePlani.objects.get(kalem['butce_plan_key'])
                butce.satin_alma_durum = 2
                butce.blocking_save()
                satin_alma.ButceKalemleri(butce=butce)
        satin_alma.aciklama = talep_form['aciklama']
        satin_alma.ad = talep_form['satin_alma_talep_adi']
        d1 = datetime.datetime.strptime(
            talep_form['teklife_acilma_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.teklife_acilma_tarihi = datetime.datetime(d1.year, d1.month, d1.day, 9, 0, 0, 0)
        d2 = datetime.datetime.strptime(
            talep_form['son_teklif_tarihi'], DATE_DEFAULT_FORMAT)
        satin_alma.teklife_kapanma_tarihi = datetime.datetime(d2.year, d2.month, d2.day, 16, 0, 0, 0
                                                              )
        satin_alma.onay_tarih_sayi = talep_form['onay_tarih_sayi']
        satin_alma.ekleyen = Personel.objects.get(talep_form['ekleyen'])
        satin_alma.ilgili_proje = proje
        satin_alma.teklif_durum = 1

        satin_alma.blocking_save()

    def basari_mesaji_goster(self):
        """
        Satın alma talebinin tamamlandığını gösteren adımdır.
        """
        form = JsonForm(title=_(u"Satın Alma Talebi"))
        form.help_text = _(u"Satın alma talebi başarıyla oluşturuldu.")
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)