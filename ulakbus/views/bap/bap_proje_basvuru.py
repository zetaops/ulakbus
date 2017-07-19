# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProjeTurleri, BAPProje, Room, Demirbas, Personel, AkademikFaaliyet
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import Okutman
from zengine.forms import JsonForm, fields
from zengine.models import WFInstance
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from pyoko import ListNode
import datetime
from ulakbus.settings import DATE_DEFAULT_FORMAT
from pyoko.fields import DATE_TIME_FORMAT


class ProjeTurForm(JsonForm):
    class Meta:
        include = ['tur']
        title = _(u'Proje Türü Seçiniz')
        always_blank = False

    # tur = fields.String(_(u"Proje Türleri"))
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
        always_blank = False

    detay_gir = fields.Button(_(u"Proje Detay Bilgileri"))


class ArastirmaOlanaklariForm(JsonForm):
    class Meta:
        title = _(u"Araştırma Olanakları Ekle")
        help_text = _(u"Üniversite/fakülte envanterinde mevcut olan ve önerilen proje ile ilgili "
                      u"kullanma olanağına sahip olduğunuz personel, yer, teçhizat (marka ve model "
                      u"belirtilerek) vs. hakkında ayrıntılı bilgi verilmelidir.")
        # always_blank = False

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
    lab_ekle = fields.Button(_(u"Ekle"), cmd='ekle')
    iptal = fields.Button(_(u"İptal"))


class DemirbasEkleForm(JsonForm):
    class Meta:
        title = _(u"Demirbaş Seç")

    demirbas = fields.String(_(u"Demirbaş"))
    demirbas_ekle = fields.Button(_(u"Ekle"), cmd='ekle')
    iptal = fields.Button(_(u"İptal"))


class PersonelEkleForm(JsonForm):
    class Meta:
        title = _(u"Personel Seç")

    personel = fields.String(_(u"Personel"))
    personel_ekle = fields.Button(_(u"Ekle"), cmd='ekle')
    iptal = fields.Button(_(u"İptal"))


class ProjeCalisanlariForm(JsonForm):
    class Meta:
        title = _(u"Çalışan Ekle")
        always_blank = False

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
        always_blank = False

    class Uzman(ListNode):
        class Meta:
            title = _(u"Uzmanlar")

        ad = fields.String(_(u"Ad"), readonly=True)
        soyad = fields.String(_(u"Soyad"), readonly=True)
        unvan = fields.String(_(u"Unvan"), readonly=True)
        kurum = fields.String(_(u"Kurum"), readonly=True)
        tel = fields.String(_(u"Telefon"), readonly=True)
        faks = fields.String(_(u"Faks"), readonly=True, required=False)
        eposta = fields.String(_(u"E-posta"), readonly=True)

    ileri = fields.Button(_(u"İleri"))


class UniversiteDisiDestekForm(JsonForm):
    class Meta:
        title = _(u"Üniversite Dışı Destek Ekle")
        always_blank = False

    class Destek(ListNode):
        class Meta:
            title = _(u"Destekler")

        kurulus = fields.String(_(u"Destekleyen Kurulus"), readonly=True)
        tur = fields.String(_(u"Destek Türü"), readonly=True)
        destek_miktari = fields.Float(_(u"Destek Miktarı"), readonly=True)
        verildigi_tarih = fields.Date(_(u"Verildiği Tarih"), format=DATE_DEFAULT_FORMAT,
                                      readonly=True)
        sure = fields.Integer(_(u"Süresi(Ay Cinsinden)"), readonly=True)
        destek_belgesi = fields.File(_(u"Destek Belgesi"), random_name=True)
        destek_belgesi_aciklamasi = fields.String(_(u"Belge Açıklaması"), required=False)

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
        always_blank = False

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
        always_blank = False

    proje_belgeleri = fields.Button(_(u"Proje Belgeleri"))


class ProjeBelgeForm(JsonForm):
    class Meta:
        include = ['ProjeBelgeleri']
        title = _(u"Proje Belgeleri")
        always_blank = False

    arastirma_olanaklari = fields.Button(_(u"Araştırma Olanakları"))


class GerceklestirmeGorevlisiForm(JsonForm):
    class Meta:
        title = _(u"Proje Gerçekleştirme Görevlisi Seçimi")
        include = ['gerceklestirme_gorevlisi']
        always_blank = False

    sec = fields.Button(_(u"Gerçekleştirme Görevlisi Seç"))


class ProjeBasvuru(CrudView):
    class Meta:
        model = "BAPProje"

    def proje_olustur(self):
        proje_id = BAPProje().blocking_save().key
        self.current.task_data['bap_proje_id'] = proje_id

    def proje_tur_sec(self):
        form = ProjeTurForm(self.object, current=self.current)
        self.form_out(form)

    def gerekli_belge_form(self):
        wfi = WFInstance.objects.get(self.current.token)
        wfi.wf_object = self.current.task_data['bap_proje_id']
        wfi.blocking_save()
        tur_id = self.current.task_data['ProjeTurForm']['tur_id']
        tur = BAPProjeTurleri.objects.get(tur_id)
        form = GerekliBelgeForm()
        if 'hedef_proje' not in self.current.task_data:
            self.current.task_data['hedef_proje'] = {}

        for belge in tur.Belgeler:
            if belge.gereklilik:
                form.BelgeForm(ad=belge.ad, gereklilik=_(u"Gerekli"))

        for proje_form in tur.Formlar:
            if proje_form.gereklilik:
                form.BelgeForm(ad=proje_form.proje_formu.ad, gereklilik=_(u"Gerekli"))

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def gerceklestirme_gorevlisi_kontrolu(self):
        """
        Seçilen proje türüne göre, gerçekleştirme görevlisinin projenin yürütücüsü ile aynı kişi 
        olması durumu kontrol edilir. Aynı kişi olması gerekiyorsa projenin gerçekleştirme 
        görevlisi, proje başvurusu yapan öğretim görevlisi olarak atanır.

        """
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        tur = BAPProjeTurleri.objects.get(td['ProjeTurForm']['tur_id'])
        if 'GerceklestirmeGorevlisiForm' in td and proje.gerceklestirme_gorevlisi.key != \
                td['GerceklestirmeGorevlisiForm']['gerceklestirme_gorevlisi_id']:
            del td['GerceklestirmeGorevlisiForm']
        aynilik_durumu = tur.gerceklestirme_gorevlisi_yurutucu_ayni_mi
        td['gerceklestirme_gorevlisi_yurutucu_ayni_mi'] = aynilik_durumu
        if aynilik_durumu:
            proje.gerceklestirme_gorevlisi = self.current.user.personel
            proje.blocking_save()

    def gerceklestirme_gorevlisi_sec(self):
        """
        Gerçekleştirme görevlisinin, proje yürütücüsünün farklı olması gereken durumda yürütücüden 
        projesi için bir gerçekleştirme görevlisi seçmesi istenir.

        """
        self.form_out(GerceklestirmeGorevlisiForm(self.object, current=self.current))

    def gorevli_secim_kontrolu(self):
        """
        Gerçekleştirme görevlisi seçim formunun boş submit edilip edilmediğini kontrol eder. Boş 
        seçilmiş ise kullanıcı bir seçim yapması yönünde uyarılır ve seçim ekranına tekrardan 
        yönlendirilir.

        """
        gorevli_id = self.input['form']['gerceklestirme_gorevlisi_id']
        self.current.task_data['gorevli_secimi_uygunlugu'] = True if gorevli_id else False

    def gorevli_secim_uyari_mesaji(self):
        """
        Uyarı mesajı oluşturulur.         

        """
        self.current.output['msgbox'] = {'type': 'warning',
                                         "title": _(u"Gerçekleştirme Görevlisi Seçimi Hatası"),
                                         "msg": _(u"İlerlemek için projenize bir gerçekleştirme "
                                                  u"görevlisi seçmelisiniz.")}

    def gerceklestirme_gorevlisi_kaydet(self):
        """
        Formdan seçilen personel, projenin gerçekleştirme görevlisi olarak kaydedilir.
                
        """
        gorevli = Personel.objects.get(self.input['form']['gerceklestirme_gorevlisi_id'])
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.gerceklestirme_gorevlisi = gorevli
        proje.blocking_save()

    def proje_genel_bilgilerini_gir(self):
        self.form_out(GenelBilgiGirForm(self.object, current=self.current))

    def proje_detay_gir(self):
        self.form_out(ProjeDetayForm(self.object, current=self.current))

    def proje_belgeleri(self):
        form = ProjeBelgeForm(self.object, current=self.current)
        self.form_out(form)
        if 'arastirma_olanaklari' not in self.current.task_data['hedef_proje']:
            self.current.task_data['hedef_proje']['arastirma_olanaklari'] = []

    def proje_belge_kaydet(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form_proje_belgeleri = self.current.task_data['ProjeBelgeForm']['ProjeBelgeleri']

        # mevcut belgeleri temizle
        proje.ProjeBelgeleri.clear()

        # formdan gelen belgeleri ekle
        for pb in form_proje_belgeleri:
            proje.ProjeBelgeleri(belge=pb['belge'], belge_aciklamasi=pb['belge_aciklamasi'])

        proje.blocking_save()
        proje.reload()

        # Dosya adını key ile form datasının içine koymuş olduk
        self.current.task_data['ProjeBelgeForm']['ProjeBelgeleri'] = proje.ProjeBelgeleri.clean_value()

    def arastirma_olanagi_ekle(self):
        form = ArastirmaOlanaklariForm(current=self.current)
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
        self.current.output["meta"]["allow_add_listnode"] = False

    def arastirma_olanagi_senkronize_et(self):
        value_map = {
            'lab': _(u"Laboratuvar"),
            'demirbas': _(u"Demirbaş"),
            'personel': _(u"Personel")
        }
        query_map = {
            'lab': Room,
            'demirbas': Demirbas,
            'personel': Personel
        }
        if len(self.current.task_data['hedef_proje']['arastirma_olanaklari']) != len(
                self.current.task_data['ArastirmaOlanaklariForm']['Olanak']):
            list_to_remove = list(self.current.task_data['hedef_proje']['arastirma_olanaklari'])
            for aotd in self.current.task_data['hedef_proje']['arastirma_olanaklari']:
                item = {
                    'ad': query_map[aotd.items()[0][0]].objects.get(aotd.items()[0][1]).__unicode__(),
                    'tur': value_map[aotd.items()[0][0]]
                }
                if item not in self.current.task_data['ArastirmaOlanaklariForm']['Olanak']:
                    list_to_remove.remove(aotd)
            self.current.task_data['hedef_proje']['arastirma_olanaklari'] = list_to_remove

    def lab_ekle(self):
        form = LabEkleForm()
        ch = prepare_choices_for_model(Room)
        form.set_choices_of('lab', ch)
        form.set_default_of('lab', ch[0][0])
        self.form_out(form)

    def demirbas_ekle(self):
        form = DemirbasEkleForm()
        ch = prepare_choices_for_model(Demirbas)
        form.set_choices_of('demirbas', ch)
        form.set_default_of('demirbas', ch[0][0])
        self.form_out(form)

    def personel_ekle(self):
        form = PersonelEkleForm()
        ch = prepare_choices_for_model(Personel)
        form.set_choices_of('personel', ch)
        form.set_default_of('personel', ch[0][0])
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
        form = ProjeCalisanlariForm(current=self.current)
        self.form_out(form)

    def universite_disi_uzman_ekle(self):
        form = UniversiteDisiUzmanForm(current=self.current)
        self.form_out(form)

    def universite_disi_destek_ekle(self):
        form = UniversiteDisiDestekForm(current=self.current)
        self.form_out(form)

    def universite_disi_destek_kaydet(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        form_destek = self.current.task_data['UniversiteDisiDestekForm']['Destek']

        for des in proje.UniversiteDisiDestek:
            tarih = des.verildigi_tarih.strftime(DATE_TIME_FORMAT)
            d = {
                'destek_belgesi': des.destek_belgesi,
                'destek_miktari': des.destek_miktari,
                'kurulus': des.kurulus,
                'sure': des.sure,
                'tur': des.tur,
                'verildigi_tarih': tarih,
                'destek_belgesi_aciklamasi': des.destek_belgesi_aciklamasi
            }

            if d not in form_destek:
                des.remove()

        # forma eklenmiş ya da düzenlenmiş belgeleri kaydettik
        for fd in form_destek:
            if 'file_content' in fd['destek_belgesi']:
                try:
                    tarih = datetime.datetime.strptime(
                        fd['verildigi_tarih'], DATE_TIME_FORMAT).date()
                except ValueError:
                    tarih = datetime.datetime.strptime(fd['verildigi_tarih'],
                                                       DATE_DEFAULT_FORMAT).date()
                proje.UniversiteDisiDestek(
                    destek_belgesi=fd['destek_belgesi'],
                    destek_miktari=fd['destek_miktari'],
                    kurulus=fd['kurulus'],
                    sure=fd['sure'],
                    tur=fd['tur'],
                    verildigi_tarih=tarih,
                    destek_belgesi_aciklamasi=fd['destek_belgesi_aciklamasi']
                )

        proje.blocking_save()
        proje.reload()

        destek_form = []
        for des in proje.UniversiteDisiDestek:
            tarih = des.verildigi_tarih.strftime(DATE_TIME_FORMAT)
            f = {
                'destek_belgesi': des.destek_belgesi,
                'destek_miktari': des.destek_miktari,
                'kurulus': des.kurulus,
                'sure': des.sure,
                'tur': des.tur,
                'verildigi_tarih': tarih,
                'destek_belgesi_aciklamasi': des.destek_belgesi_aciklamasi
            }
            destek_form.append(f)

        # Dosya adını key ile form datasının içine koymuş olduk
        self.current.task_data['UniversiteDisiDestekForm']['Destek'] = destek_form

    def yurutucu_tecrubesi(self):
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
        personel = Personel.objects.get(user_id=self.current.user_id)
        projeler = BAPProje.objects.all(yurutucu=Okutman.objects.get(personel=personel))

        form = YurutucuProjeForm(current=self.current)

        for proje in projeler:
            if proje.UniversiteDisiDestek:
                kurum = proje.UniversiteDisiDestek[0].kurulus
                miktar = proje.UniversiteDisiDestek[0].destek_miktari
            else:
                kurum = None
                miktar = None
            form.Proje(ad=proje.ad, kurum=kurum, miktar=miktar)

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def proje_kaydet(self):
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        yurutucu = Okutman.objects.get(personel=Personel.objects.get(user_id=self.current.user_id))
        proje.yurutucu = yurutucu
        if 'arastirma_olanaklari' in td['hedef_proje']:
            proje.ArastirmaOlanaklari.clear()
            for olanak in td['hedef_proje']['arastirma_olanaklari']:
                if 'lab' in olanak:
                    proje.ArastirmaOlanaklari(lab_id=olanak['lab'], demirbas=None, personel=None)
                elif 'demirbas' in olanak:
                    proje.ArastirmaOlanaklari(lab=None, demirbas_id=olanak['demirbas'],
                                              personel=None)
                else:
                    proje.ArastirmaOlanaklari(lab=None, demirbas=None,
                                              personel_id=olanak['personel'])
        if 'GenelBilgiGirForm' in td:
            proje.ad = td['GenelBilgiGirForm']['ad']
            proje.anahtar_kelimeler = td['GenelBilgiGirForm'][
                'anahtar_kelimeler']
            proje.sure = td['GenelBilgiGirForm']['sure']
            proje.teklif_edilen_baslama_tarihi = datetime.datetime.strptime(
                td['GenelBilgiGirForm']['teklif_edilen_baslama_tarihi'],
                DATE_DEFAULT_FORMAT)
            proje.teklif_edilen_butce = td['GenelBilgiGirForm'][
                'teklif_edilen_butce']
        if 'ProjeDetayForm' in td:
            proje.b_plani = td['ProjeDetayForm']['b_plani']
            proje.hedef_ve_amac = td['ProjeDetayForm']['hedef_ve_amac']
            proje.basari_olcutleri = td['ProjeDetayForm']['basari_olcutleri']
            proje.ozgun_deger = td['ProjeDetayForm']['ozgun_deger']
            proje.konu_ve_kapsam = td['ProjeDetayForm']['konu_ve_kapsam']
            proje.literatur_ozeti = td['ProjeDetayForm']['literatur_ozeti']
            proje.yontem = td['ProjeDetayForm']['yontem']
        if 'ProjeTurForm' in td:
            proje.tur_id = str(td['ProjeTurForm']['tur_id'])
        if 'ProjeCalisanlariForm' in td:
            proje.ProjeCalisanlari.clear()
            for calisan in td['ProjeCalisanlariForm']['Calisan']:
                proje.ProjeCalisanlari(ad=calisan['ad'], soyad=calisan['soyad'],
                                       nitelik=calisan['nitelik'],
                                       calismaya_katkisi=calisan['calismaya_katkisi'])
        if 'UniversiteDisiUzmanForm' in td:
            proje.UniversiteDisiUzmanlar.clear()
            for uzman in td['UniversiteDisiUzmanForm']['Uzman']:
                proje.UniversiteDisiUzmanlar(
                    ad=uzman['ad'],
                    soyad=uzman['soyad'],
                    unvan=uzman['unvan'],
                    kurum=uzman['kurum'],
                    tel=uzman['tel'],
                    faks=uzman['faks'],
                    eposta=uzman['eposta']
                )

        proje.ProjeIslemGecmisi(eylem=_(u"Kayıt"),
                                aciklama=_(u"Öğretim üyesi tarafından kaydedildi"),
                                tarih=datetime.datetime.now())
        proje.durum = 1
        if not proje.basvuru_rolu.exist:
            proje.basvuru_rolu = self.current.role
        proje.blocking_save()

    def proje_goster(self):
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.show()
        form = JsonForm()
        form.onay = fields.Button(_(u"Onaya Gönder"), cmd='onay')
        self.form_out(form)

    def onaya_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.durum = 2
        proje.ProjeIslemGecmisi(eylem=_(u"Onaya Gönderildi"),
                                aciklama=_(u"Koordinasyon Birimine onaya gönderildi"),
                                tarih=datetime.datetime.now())
        proje.blocking_save()

    def bildirim_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        role = proje.yurutucu().okutman().user().role_set[0].role
        if self.cmd == 'iptal' or self.current.task_data['karar'] == 'iptal':
            role.send_notification(
                title=_(u"Proje Başvuru Durumu: %s" % proje.ad),
                message=_(u"%s adlı proje başvurunuz koordinasyon birimine iletilmiştir. "
                          u"En kısa sürede incelenip bilgilendirme yapılacaktır." % proje.ad),
                sender=self.current.user
            )
            karar = 'iptal'
            help_text = _(u"%s adlı projeye daha sonra karar vermeyi seçtiniz. Başvuru Listeleme iş "
                     u"akışından bu projeye ulaşabilirsiniz." % proje.ad)

        elif self.current.task_data['karar'] == 'onayla':
            role.send_notification(
                title=_(u"Proje Başvuru Durumu: %s" % proje.ad),
                message=_(u"%s adlı proje başvurunuz koordinasyon birimi tarafından onaylanarak gündeme "
                          u"alınmıştır." % proje.ad),
                sender=self.current.user
            )
            karar = 'onayla'
            help_text = _(u"%s adlı projeyi onayladınız. Kararınızı değiştirmek istiyorsanız Başvuru "
                     u"Listeleme iş akışından bu projeye ulaşabilirsiniz." % proje.ad)
        else:
            karar = 'revizyon'
            help_text = _(u"%s adlı projeyi revizyona gönderdiniz. %s, revizyon talebi hakkında "
                     u"bilgilendirildi." % (proje.ad, proje.yurutucu))
        form = JsonForm(title=_(u"%s Hakkındaki Kararınız" % proje.ad))
        form.help_text = help_text
        form.tamam = fields.Button(_(u"Tamam"), cmd=karar)
        self.form_out(form)

    def revizyon_mesaji_goster(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        baslik = _(u"#### Revizyon Gerekçeleri:\n")
        msg = self.current.task_data['revizyon_gerekce']
        form = JsonForm(title=_(u"%s İsimli Proje İçin Revizyon Talebi" % proje.ad))
        form.help_text = baslik + msg
        form.devam = fields.Button(_(u"Revize Et"))
        self.form_out(form)


