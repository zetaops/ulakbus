# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPTeklif, BAPButcePlani, BAPTeklifFiyatIsleme
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.s3_file_manager import S3FileManager
from datetime import datetime, time
from ulakbus.settings import DATETIME_DEFAULT_FORMAT


class KazananFirmalarForm(JsonForm):
    """
    Bütçe kalemleri için kazanan firmaların belirlenmesi formunu oluşturur.

    """

    class Meta:
        inline_edit = ['firma']
        title = __(u"{} İçin Kazanan Firmaların Belirlenmesi")
        help_text = __(u"Lütfen listelenmiş bütçe kalemleri için kazanan firmayı seçiniz. "
                       u"Kazanan bir firma bulunmuyor ise boş bırakınız.")
        always_blank = False

    class KazananFirmalar(ListNode):
        class Meta:
            title = __(u"Kazanan Firmalar")

        kalem = fields.String(__(u"Bütçe Kalemi Adı"))
        adet = fields.Integer(__(u"Adet"))
        firma = fields.String(__(u"Kazanan Firma"))
        key = fields.String('Key', hidden=True)

    ilerle = fields.Button(__(u"İlerle"), cmd='ilerle')
    geri = fields.Button(__(u"Teklif Görüntüleme Ekranına Geri Dön"), cmd='geri_don')


class KazananFirmalarGosterForm(KazananFirmalarForm):
    """
    KazananFirmalarForm un read only olarak gösterilmesi için kalıtım formu.

    """

    class Meta:
        inline_edit = []
        always_blank = False

    KazananFirmalar = KazananFirmalarForm.KazananFirmalar
    ilerle = fields.Button(__(u"Onayla"), cmd='onayla')
    geri = fields.Button(__(u"Kazanan Belirleme Ekranına Geri Dön"), cmd='geri_don')


class TeklifGorForm(JsonForm):
    """
    Seçilen satın alma duyurusuna yapılmış tekliflerin gösterildiği form.

    """

    class Meta:
        title = __(u"{} Satın Alma Duyurusu Teklifleri")

    degerlendir = fields.Button(__(u"Teklifleri Değerlendir"), cmd='degerlendir')
    indir = fields.Button(__(u"Bütün Teklif Dosyalarını İndir"), cmd='indir')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class KararVerForm(JsonForm):
    """
    Karar verme ekranına gitmek için kullanılan form.

    """

    class Meta:
        title = __(u"{} Satın Alma Duyurusuna Verilen Teklifler")

    belirle = fields.Button(__(u"Kazanan Firmaları Belirle"), cmd='belirle')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class TeklifIsleForm(JsonForm):
    """
    Tekliflerin işlenmesi için kullanılan form.

    """

    class Meta:
        inline_edit = ['birim_fiyat']
        title = __(u"{} Firması {} Satın Alma Duyurusu Fiyat İşlemeleri")
        help_text = __(u"Firmanın teklifte bulunduğu bütçe kalemleri için gereken yerleri "
                       u"doldurunuz. Teklif verilmeyen kalemlerin alanlarını boş bırakınız.")

    class TeklifIsle(ListNode):
        class Meta:
            title = __(u"Teklif Fiyat İşlemeleri")

        kalem = fields.String(__(u"Bütçe Kalemi Adı"))
        adet = fields.Integer(__(u"Adet"))
        birim_fiyat = fields.Float(__(u" Birim Fiyat"))
        key = fields.String('Key', hidden=True)

    kaydet = fields.Button(__(u"Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class SatinAlmaBilgileriDuzenleForm(JsonForm):
    """
         Seçilen satın alma duyurusuna ait teklife kapanma tarihi ve isim bilgilerini düzenleme
         işlemini içerir.
    """

    class Meta:
        include = ['ad', 'teklife_acilma_tarihi', 'teklife_kapanma_tarihi', 'aciklama']
        title = _(u'Duyuru Bilgileri Düzenle')

    kaydet = fields.Button(__(u"Kaydet"), cmd="kaydet")
    geri_don = fields.Button(__(u"Geri Dön"), cmd="geri_don")


class ButceKalemiBilgileriForm(JsonForm):
    class Meta:
        inline_edit = ['satin_alma_durum']

    class KalemBilgileri(ListNode):
        class Meta:
            title = __(u"Bütçe Kalemi Bilgileri")

        ad = fields.String(__(u"Ad"))
        adet = fields.Integer(__(u"Adet"))
        satin_alma_durum = fields.Integer(__(u"Satın Alma Durumu"),
                                          choices='bap_butce_plani_satin_alma_durumu', default=None)
        key = fields.String('Key', hidden=True)

    guncelle = fields.Button(__(u"Güncelle"), cmd="satin_alma_islemler")
    geri_don = fields.Button(__(u"Geri Dön"), cmd="geri_don")


class TeklifDegerlendirme(CrudView):
    """
    Seçilen satın alma duyurusuna yapılmış tekliflerin değerlendirildiği view.

    """

    class Meta:
        model = 'BAPSatinAlma'

    def _list(self):
        """
        Koordinasyon birimi görevlisinin kendi üstünde bulunan satın alma duyurularını listeler.

        """
        form = JsonForm(title=__(u"Satın Alma Duyurularının Listesi"))
        self.list(custom_form=form)

    def teklifleri_gor(self):
        """
        Seçilen satın alma duyurusuna teklif yapmış firmalar listelenir.

        """
        self.output['objects'] = [[_(u'Firma Adı')]]
        for teklif in BAPTeklif.objects.filter(satin_alma=self.object).order_by():
            name, cmd = (_(u'Teklif Fiyatları Düzenle'), 'duzenle') if teklif.fiyat_islemesi else (
                _(u'Teklif Fiyatları İşle'), 'isle')
            list_item = {
                "fields": [teklif.firma.ad],
                "actions": [
                    {'name': name, 'cmd': cmd, 'show_as': 'button', 'object_key': 'data_key'}
                ],
                'key': teklif.key}

            self.output['objects'].append(list_item)

        form = TeklifGorForm(current=self.current)
        form.title = form.title.format(self.object.ad)
        self.form_out(form)

    def belge_indir(self):
        """
        Duyuruya teklif vermiş bütün firmaların teklifleri topluca bir zip dosyası halinde
        indirilir.

        """
        teklifler = BAPTeklif.objects.filter(satin_alma=self.object)
        keys = [belge.belge for teklif in teklifler for belge in teklif.Belgeler]
        s3 = S3FileManager()
        zip_url = s3.download_files_as_zip(keys, "{}FirmaTeklifBelgeleri".format(self.object.ad))
        self.set_client_cmd('download')
        self.current.output['download_url'] = zip_url

    def teklifleri_isle_duzenle(self):
        """
        Firmaların verdiği teklifler birim fiyatolarak işlenir. Adet ve birim fiyat kullanılarak
        toplam fiyat hesaplanir. Eğer önceden işlenmiş ise düzenlenebilir.

        """
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False

        firma = BAPTeklif.objects.get(self.input['data_key']).firma
        self.current.task_data['teklif_id'] = self.input['data_key']

        form = TeklifIsleForm(current=self.current)
        form.title = form.title.format(firma.ad, self.object.ad)
        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            kwargs = {'kalem': kalem.ad,
                      'adet': kalem.adet,
                      'key': kalem.key,
                      'birim_fiyat': None,
                      }

            if self.cmd == 'duzenle':
                fiyat = BAPTeklifFiyatIsleme.objects.get_or_none(**{'kalem': kalem, 'firma': firma})
                if fiyat:
                    kwargs.update({'birim_fiyat': fiyat.birim_fiyat})

            form.TeklifIsle(**kwargs)

        self.form_out(form)

    def teklif_islemeleri_kaydet(self):
        """
        Yeni girilen teklif işlemeleri ya da düzenlenen teklif işlemeleri kaydedilir. Teklife ilk
        defa işleme yapılıyor ise fiyat işlemesi fieldı True yapılır.

        """
        teklif = BAPTeklif.objects.get(self.current.task_data['teklif_id'])
        self.current.task_data['firma_ad'] = teklif.firma.ad
        for obj in self.input['form']['TeklifIsle']:
            teklif_bilgileri = {'firma_id': teklif.firma.key,
                                'kalem_id': obj['key'],
                                'satin_alma_id': self.object.key}

            if not obj['birim_fiyat']:
                BAPTeklifFiyatIsleme.objects.delete_if_exists(**teklif_bilgileri)
                continue

            isleme, new = BAPTeklifFiyatIsleme.objects.get_or_create(**teklif_bilgileri)
            teklif.fiyat_islemesi = True

            isleme(birim_fiyat=float(obj['birim_fiyat']),
                   toplam_fiyat=float(obj['birim_fiyat']) * obj['adet']).save()

        teklif.save()

    def islem_mesaji_olustur(self):
        """
        Teklif işleme kaydetme ya da düzenleme işleminden sonra başarılı işlem mesajı gösterilir.

        """
        islem_mesaji = _(u"{} firmasının teklif işleme işlemi başarıyla gerçekleştirilmiştir. "
                         u"Düzenleme butonuna basarak girmiş olduğunuz bilgileri "
                         u"düzenleyebilirsiniz.".format(self.current.task_data['firma_ad']))
        self.current.output['msgbox'] = {'type': 'info',
                                         "title": _(u"İşlem Mesajı"),
                                         "msg": islem_mesaji}

    def degerlendirme_kontrol(self):
        """
        Tekliflerin değerlendirilebilmesi için duyuruya yapılmış bütün tekliflerin işlemelerinin
        yapılmış olması gerekmektedir. Bu durum kontrol edilir.

        """
        teklifler = BAPTeklif.objects.filter(satin_alma=self.object, fiyat_islemesi=False)
        self.current.task_data['degerlendirme_kontrol'] = False if teklifler else True

    def degerlendirme_hata_mesaji_olustur(self):
        """
        Eğer işlemesi yapılmayan teklifler varken değerlendirme yapılması denenirse önce
        işlemelerin yapılması gerektiği hakkında uyarı mesajı oluşturulur.

        """
        hata_mesaji = _(u"'{}' adlı satın almaya ait teklif fiyatları işlemediğiniz firmalar "
                        u"bulunmaktadır. Karar vermeden önce lütfen teklif veren tüm firmaların "
                        u"tekliflerini işleyiniz.".format(self.object.ad))
        self.current.output['msgbox'] = {'type': 'warning',
                                         "title": _(u"Hata Mesajı"),
                                         "msg": hata_mesaji}

    def teklifleri_degerlendir(self):
        """
        Bütçe kalemlerine firmaların verdiği teklifler toplam fiyat olarak gösterilir.

        """
        self.current.output["meta"]["allow_actions"] = False
        form = KararVerForm(current=self.current)
        form.title = form.title.format(self.object.ad)

        self.output['objects'] = [[_(u'Kalem Adı'), _(u'Adet')]]
        firmalar = [teklif.firma for teklif in
                    BAPTeklif.objects.filter(satin_alma=self.object).order_by()]
        self.current.task_data['firma_adlari'] = [(firma.key, firma.ad) for firma in firmalar]
        self.output['objects'][0].extend([firma.ad for firma in firmalar])

        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            list_item = {
                "fields": [kalem.ad,
                           str(kalem.adet)],
                "actions": '',
            }
            for firma in firmalar:
                fiyat = BAPTeklifFiyatIsleme.objects.get_or_none(**{'kalem': kalem, 'firma': firma})
                list_item['fields'].append(str(fiyat.toplam_fiyat) if fiyat else '-')

            self.output['objects'].append(list_item)
        self.form_out(form)

    def kazanan_firmalari_belirle(self):
        """
        Seçilen satın alma duyurusunda bulunan her bir bütçe kalemi için kazanan firma belirlenir.

        """
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False
        form = KazananFirmalarForm(current=self.current)
        form.title = form.title.format(self.object.ad)
        form.KazananFirmalar._fields['firma'].choices = self.current.task_data['firma_adlari']

        for kalem in self.object.ButceKalemleri:
            kalem = kalem.butce
            form.KazananFirmalar(kalem=kalem.ad,
                                 adet=kalem.adet,
                                 key=kalem.key)

        self.form_out(form)

    def onaylama_ekrani_goster(self):
        """
        Seçimlerin onaylanmadan önce son kontrol için bütçe kalemleri için seçilen kazanan firma
        gösterilir.

        """
        self.current.output["meta"]["allow_add_listnode"] = False
        self.current.output["meta"]["allow_actions"] = False
        help_text = __(u"{} satın alma duyurusunda bulunan bütçe kalemleri için belirlediğiniz "
                       u"kazanan firmalar aşağıda listelenmiştir. Değişiklik yapmak için bir "
                       u"önceki ekrana dönebilir, kaydetmek için Onayla butonuna basarak "
                       u"ilerleyebilirsiniz.").format(self.object.ad)

        self.current.task_data['KazananFirmalarGosterForm'] = self.current.task_data[
            'KazananFirmalarForm']

        form = KazananFirmalarGosterForm(current=self.current,
                                         title=__(u'Kazanan Firmaların Onayı'))
        form.help_text = help_text

        self.form_out(form)

    def kazanan_firma_kaydet(self):
        """
        Onaylanırsa, her bir bütçe kalemi için seçilmiş kazanan firma kaydedilir.

        """
        self.object.teklif_durum = 3
        self.object.blocking_save({'teklif_durum': 3})
        for obj in self.input['form']['KazananFirmalar']:
            if obj['firma']:
                kalem = BAPButcePlani.objects.get(obj['key'])
                teklif = BAPTeklif.objects.get(firma_id=str(obj['firma']), satin_alma=self.object)
                kalem.kazanan_firma_id = str(obj['firma'])
                teklif.durum = 3
                teklif.save()
                kalem.save()

    def islem_mesaji_goster(self):
        """
        Kaydedilme işleminden sonra, başarılı işlem mesajı gösterilir.

        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Bilgilendirme'),
            "msg": _(u'{} adlı satın alma duyurusu için teklifler değerlendirildi ve kazanan '
                     u'firma/firmalar belirlendi.'.format(self.object.ad))}

    def teklife_kapat(self):
        """
        Durumu Teklife Açık olan satın alma duyurusunun durumunu Teklife Kapalı olarak
        değiştirir.

        """
        self.object.teklif_durum = 2
        self.object.blocking_save({'teklif_durum': 2})
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'İşlem Bilgilendirme'),
            "msg": _(
                u'{} adlı satın alma duyurusu teklife kapatıldı. Teklifleri Değerlendir butonuna '
                u'tıklayarak duyuruya ait teklifleri değerlendirebilirsiniz.'.format(
                    self.object.ad))}

    def satin_alma(self):
        """
        Seçili olan satın alma duyurusuna ait bütçe kalemlerinin bilgilerini listeler.

        """
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False
        form = ButceKalemiBilgileriForm(title="{} Bütçe Kalemlerinin Bilgileri".format(self.object.ad))
        for kalem in self.object.ButceKalemleri:
            form.KalemBilgileri(ad=kalem.butce.ad, adet=kalem.butce.adet,
                                satin_alma_durum=kalem.butce.satin_alma_durum, key=kalem.butce.key)
        self.form_out(form)

    def satin_alma_islemler(self):
        """
        Seçili olan satın alma duyurusunun satın alma durumunun belirlenmesi işlemini içerir.

        """
        for obj in self.input["form"]["KalemBilgileri"]:
            kalem = BAPButcePlani.objects.get(obj["key"])

            if obj["satin_alma_durum"] == 4:
                try:
                    BAPTeklifFiyatIsleme.objects.get(kalem=kalem, firma=kalem.kazanan_firma)
                    kalem.satin_alma_durum = obj["satin_alma_durum"]
                except ObjectDoesNotExist:
                    pass
            else:
                kalem.satin_alma_durum = obj["satin_alma_durum"]
            kalem.save()

    def satin_alma_bilgilerini_duzenle(self):
        """
        Seçili olan satın alma duyurusunun bilgilerini düzenleme işlemini içerir.

        """
        form = SatinAlmaBilgileriDuzenleForm(self.object, current=self.current)
        self.form_out(form)

    def degisiklikleri_kaydet(self):
        """
        Seçilen satın alma duyurusunda yapılan değişiklikleri kaydetme işlemini içerir.

        """
        tat = "{} {}".format(self.input["form"]["teklife_acilma_tarihi"], time(17))
        tkt = "{} {}".format(self.input["form"]["teklife_kapanma_tarihi"], time(17))
        self.object.teklife_acilma_tarihi = datetime.strptime(tat, DATETIME_DEFAULT_FORMAT)
        self.object.teklife_kapanma_tarihi = datetime.strptime(tkt, DATETIME_DEFAULT_FORMAT)
        self.object.ad = self.input["form"]["ad"]
        self.object.aciklama = self.input['form']['aciklama']
        self.object.save()

    @obj_filter
    def satin_alma_duyurulari_actions(self, obj, result):
        """
        Satın Alma Duyurularının butonları 4 duruma göre eklenir.
        1) Düzenle: Durumu Teklife açık olan ve teklife kapanma tarihi sonlanmayan duyurular için.
        2) Teklife Kapat: Durumu Teklife açık olan ve teklife kapanma tarihi sonlanan duyurular için.
        3) Teklifleri Değerlendir: Durumu Teklife Kapalı olan duyurular için.
        4) Satın Alma Gerçekleştir: Durumu Değerlendirildi olan duyurular için.

        data(dict): Buton ismi ve cmd değerlerini içerir. Gelen nesnenin teklif durumuna göre
        datadaki veriler kullanılır.

        """
        data = {1: {"name": "Teklife Kapat", "cmd": "teklife_kapat"},
                2: {"name": "Teklifleri Değerlendir", "cmd": "degerlendir"},
                3: {"name": "Satın Alma Bilgilerini Güncelle", "cmd": "satin_alma"}}
        if obj.teklif_durum == 1 and obj.teklife_kapanma_tarihi < datetime.now():
            result['actions'] = [{'name': "Düzenle", 'cmd': "duzenle", "mode": "normal",
                                  "show_as": "button"}]
        else:
            result['actions'] = [{"name": data[obj.teklif_durum]["name"],
                                  "cmd": data[obj.teklif_durum]["cmd"], "mode": "normal",
                                  "show_as": "button"}]

    @list_query
    def satin_alma_duyurularini_listele(self, queryset):
        """
        Sorumluya gösterilecek satın alma duyuruları listelenir.

        """
        return queryset.filter(sorumlu=self.current.role).order_by()
