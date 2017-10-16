# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import IntegrityError, ObjectDoesNotExist
from ulakbus.models import BAPProjeTurleri, BAPProje, Room, Demirbas, Personel, AkademikFaaliyet, \
    BAPRapor
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import Okutman
from ulakbus.models import Role
from zengine.forms import JsonForm, fields
from zengine.models import TaskInvitation
from zengine.models import WFInstance
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from pyoko import ListNode
from datetime import datetime, timedelta
from ulakbus.settings import DATE_DEFAULT_FORMAT
from pyoko.fields import DATE_TIME_FORMAT
from dateutil.relativedelta import relativedelta


class ProjeTurForm(JsonForm):
    class Meta:
        title = _(u'Proje Türü Seçiniz')
        always_blank = False

    tur = fields.String(_(u"Proje Türleri"), required=True)
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
        include = ['ad', 'sure', 'anahtar_kelimeler', 'teklif_edilen_butce']
        title = _(u"Proje Genel Bilgileri")
        always_blank = False

    daha_sonra_devam_et = fields.Button(_(u"Daha Sonra Devam Et"), cmd='daha_sonra_devam_et',
                                        form_validation=False)
    detay_gir = fields.Button(_(u"Proje Detay Bilgileri"), cmd='detay_gir')


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

    daha_sonra_devam_et = fields.Button(_(u"Daha Sonra Devam Et"), cmd='daha_sonra_devam_et',
                                        form_validation=False)
    lab_ekle = fields.Button(_(u"Laboratuvar Ekle"), cmd='lab')
    demirbas_ekle = fields.Button(_(u"Demirbas Ekle"), cmd='demirbas')
    personel_ekle = fields.Button(_(u"Personel Ekle"), cmd='personel')
    ileri = fields.Button(_(u"İleri"), cmd='ilerle')


class LabEkleForm(JsonForm):
    class Meta:
        title = _(u"Laboratuvar Seç")

    lab = Room()
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

    personel = Personel()
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
        kurum = fields.String(_(u"Kurum"), readonly=True)

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

    daha_sonra_devam_et = fields.Button(_(u"Daha Sonra Devam Et"), cmd='daha_sonra_devam_et',
                                        form_validation=False)
    ileri = fields.Button(_(u"İleri"), cmd='ileri')


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

    daha_sonra_devam_et = fields.Button(_(u"Daha Sonra Devam Et"), cmd='daha_sonra_devam_et',
                                        form_validation=False)
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
    """
    Öğretim üyesinin bilimsel araştırma proje başvurusu yaptığı iş akışıdır.
    """

    class Meta:
        model = "BAPProje"

    def rapor_kontrol(self):
        """
        Projelere ait raporlar istenen sürede verildi mi kontrolü yapılır.
        Birinci kontrol, süresi gelen sonuç raporunun verilmiş olması durumu ve
        rapor süresi gelmeyen projenin durumunu içerir. İlk dönem süresi kontrolü için proje başlama
        tarihine 6 ay eklenerek kontrol yapılır.
        İkinci kontrol ise süresi gelen dönem raporunun olmaması durumunu içerir. Dönem rapor süresi
        gecen süre 6 aya bölünerek bulunur.

        """
        okutman = Okutman.objects.get(personel=self.current.user.personel)
        projeler = BAPProje.objects.filter(yurutucu=okutman)
        kontrol = True
        for proje in projeler:
            bitis_suresi = proje.kabul_edilen_baslama_tarihi + relativedelta(months=proje.sure)
            ilk_donem_suresi = proje.kabul_edilen_baslama_tarihi + relativedelta(months=6)
            if BAPRapor.objects.filter(proje=proje, tur=2, olusturulma_tarihi__gte=bitis_suresi) \
                    or ilk_donem_suresi > datetime.now().date():
                continue
            gecen_sure = datetime.now().date() - proje.kabul_edilen_baslama_tarihi
            donem_suresi = proje.kabul_edilen_baslama_tarihi + relativedelta(
                months=gecen_sure.days / 180)
            if not BAPRapor.objects.filter(proje=proje, tur=1,
                                           olusturulma_tarihi__gte=donem_suresi):
                kontrol = False
                self.current.task_data['proje_id'] = proje.key
                break
        self.current.task_data['kontrol'] = kontrol

    def rapor_bilgilendirme(self):
        """
        Öğretim üyesine projelerinde rapor süresi geçen bir projesi olduğuna dair bilgi
        mesajı gösterilir.

        """
        proje = BAPProje.objects.get(self.current.task_data['proje_id'])
        form = JsonForm(title=_(u"Sonuç Raporu Bilgilendirme"))
        form.help_text = "%s projenize ait rapor yükleme süresi geçmiştir. Lütfen proje başvurusu yapabilmek için raporunuzu yükleyiniz." % (
            proje.ad)
        form.yonlendir = fields.Button(_(u"Anasayfaya Git"))
        self.form_out(form)

    def anasayfaya_yonlendir(self):
        """
        Anasayfaya yönlendirme işlemini gerçekleştirir.

        """
        self.current.output['cmd'] = 'reload'

    def proje_tur_sec(self):
        """
        Proje türünün seçildiği adımdır.
        Makine teçhizat ekle adımı için task_data'ya proje_basvuru değeri True olarak eklenir.
        """
        self.current.task_data['proje_basvuru'] = True
        form = ProjeTurForm(current=self.current)
        choices = prepare_choices_for_model(BAPProjeTurleri)
        form.set_choices_of('tur', choices)
        form.set_default_of('tur', choices[0][0])
        self.form_out(form)

    def gerekli_belge_form(self):
        """
        Proje türü için gerekli belgelerin gösterildiği, öğretim üyesinin belgelerini kontrol ederek
        belgelerinin hazır olduğunu beyan ettiği adımdır. Belgeler hazırsa proje genel bilgileri
        adımına geçilir, hazır değilse proje türü adımına geri dönülür.
        """
        tur_id = self.current.task_data['ProjeTurForm']['tur']
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
        tur = BAPProjeTurleri.objects.get(td['ProjeTurForm']['tur'])
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
        """
        Proje genel bilgilerinin girildiği adımdır.
        """
        self.form_out(GenelBilgiGirForm(self.object, current=self.current))

    def proje_no_kaydet(self):
        """
        Genel bilgi gir adımından sonra proje bir proje nuarası oluşturularak kaydedilir. Projeler
        türleri üzerinde numaralandırılır. Proje üzerinde son kaydedilmiş projenin proje_no alanı
        değerinin bir fazlası bir sonraki projenin proje_no'su olarak kaydedilir.

        Örnek: Altyapı projeleri için proje tür kodu ALT olacağı
        için numaralandırma artan bir şekilde devam ettiğinde kaydedilecek projeler ALT1, ALT2,
        ALT3... şeklinde numaralandırılacaktır.

        Proje türü ve proje numarası unique_together olduğundan kayıt sırasında IntegrityError
        beklenir. Eğer IntegrityError yakalanırsa, sorgu tekrar atılır ve tekrar kayıt yapılır.

        """
        if self.current.task_data['cmd'] == 'retry':
            self.current.task_data['cmd'] = self.current.task_data['pre_cmd']
        tur_id = self.current.task_data['ProjeTurForm']['tur']
        proje_id = self.current.task_data.get('bap_proje_id', False)
        if proje_id:
            proje = BAPProje.objects.get(proje_id)
            if proje.tur.key != tur_id:
                proje.proje_no = self.proje_no_belirle(tur_id)
        else:
            proje = BAPProje()
            proje.proje_no = self.proje_no_belirle(tur_id)
        proje.tur = BAPProjeTurleri.objects.get(tur_id)
        try:
            proje.blocking_save()
        except IntegrityError:
            self.current.task_data['pre_cmd'] = self.current.task_data['cmd']
            self.current.task_data['cmd'] = 'retry'
        proje_id = proje.key
        self.current.task_data['bap_proje_id'] = proje_id

        wfi = WFInstance.objects.get(self.current.token)
        wfi.wf_object = proje_id
        wfi.blocking_save()

    def proje_no_belirle(self, tur_id):
        """
        Proje ve türe özgü proje_no alanının belirlendiği adımdır.
        """
        r = BAPProje.objects.set_params(rows=1).filter(tur_id=tur_id).order_by(
            '-proje_no').values_list('proje_no')
        r.extend(BAPProje.objects.set_params(rows=1).filter(tur_id=tur_id, deleted=True).order_by(
            '-proje_no').values_list('proje_no'))
        return max(r) + 1 if r else 1

    def kaydet_ve_draft_olustur(self):
        """
        Öğretim üyesinin projeye daha sonra devam etmek istediği takdirde çalışacak adımdır.
        Projenin tur ve proje_no alanları kaydedilir. Çalışan wfi instance'ı ile bir TaskInvitation
        oluşturularak kullanıcının görev yöneticisine projenin en baştan formları dolu bir şekilde
        devam edebileceği bir task koyulur. Proje başvurusu tamamlandığında bu task görev
        yöneticisinden silinecektir.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        today = datetime.today()
        wfi = WFInstance.objects.get(self.current.token)
        role = Role.objects.get(user=self.current.user)
        inv = TaskInvitation.objects.get_or_none(role=role, instance=wfi)
        if not inv:
            inv = TaskInvitation(
                instance=wfi,
                role=role,
                wf_name=wfi.wf.name,
                progress=30,
                start_date=today,
                finish_date=today + timedelta(15)
            )
        inv.title = "%s | %s" % (proje.proje_kodu, wfi.wf.title)
        inv.blocking_save()
        self.current.output['cmd'] = 'reload'

    def proje_detay_gir(self):
        """
        Proje detay bilgilerinin girildiği adımdır.
        """
        self.object.ad = self.input['form']['ad']
        self.object.blocking_save()
        self.form_out(ProjeDetayForm(self.object, current=self.current))

    def proje_belgeleri(self):
        """
        Proje belgelerinin eklendiği adımdır.
        """
        form = ProjeBelgeForm(self.object, current=self.current)
        self.form_out(form)
        if 'arastirma_olanaklari' not in self.current.task_data['hedef_proje']:
            self.current.task_data['hedef_proje']['arastirma_olanaklari'] = []

    def proje_belge_kaydet(self):
        """
        Eklenen proje belgelerinin kaydedildiği adımdır.
        """
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
        self.current.task_data['ProjeBelgeForm'][
            'ProjeBelgeleri'] = proje.ProjeBelgeleri.clean_value()

    def arastirma_olanagi_ekle(self):
        """
        Araştırma olanaklarının proje başvurusuna eklendiği adımdır.
        Bu adımda demirbaş, personel ve laboratuvar proje başvurusuna eklenebilir.
        """
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
        """
        Submit edilen form ile kaydedilecek araştırma olanaklarını senkronize eden adımdır.
        """
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
                    'ad': query_map[aotd.items()[0][0]].objects.get(
                        aotd.items()[0][1]).__unicode__(),
                    'tur': value_map[aotd.items()[0][0]]
                }
                if item not in self.current.task_data['ArastirmaOlanaklariForm']['Olanak']:
                    list_to_remove.remove(aotd)
            self.current.task_data['hedef_proje']['arastirma_olanaklari'] = list_to_remove

    def lab_ekle(self):
        """
        Öğretim üyesinin laboratuvar arayıp başvurusuna dahil ettiği adımdır.
        """
        form = LabEkleForm(current=self.current)
        self.form_out(form)

    def personel_ekle(self):
        """
        Öğretim üyesinin personel arayıp başvurusuna dahil ettiği adımdır.
        """
        form = PersonelEkleForm(current=self.current)
        self.form_out(form)

    def olanak_kaydet(self):
        """
        Araştırma olanaklarının task_data'ya kaydedildiği adımdır.
        """
        if 'form' in self.input and 'lab_id' in self.input['form']:
            olanak = {'lab': self.input['form']['lab_id']}
        elif 'demirbas' in self.current.task_data:
            olanak = {'demirbas': self.current.task_data.pop('demirbas')}
        else:
            olanak = {'personel': self.input['form']['personel_id']}

        self.current.task_data['hedef_proje']['arastirma_olanaklari'].append(olanak)

    def calisan_ekle(self):
        """
        Proje çalışanlarının eklendiği adımdır.
        """
        form = ProjeCalisanlariForm(current=self.current)
        self.form_out(form)

    def universite_disi_uzman_ekle(self):
        """
        Proje başvurusuna üniversite dışı uzman eklendiği adımdır.
        """
        form = UniversiteDisiUzmanForm(current=self.current)
        self.form_out(form)

    def universite_disi_destek_ekle(self):
        """
        Proje başvurusuna üniversite dışı destek eklendiği adımdır.
        """
        form = UniversiteDisiDestekForm(current=self.current)
        self.form_out(form)

    def universite_disi_destek_kaydet(self):
        """
        Universite dışı desteklerin kaydedildiği adımdır.
        """
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
                    tarih = datetime.strptime(
                        fd['verildigi_tarih'], DATE_TIME_FORMAT).date()
                except ValueError:
                    tarih = datetime.strptime(fd['verildigi_tarih'],
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
        """
        Öğretim üyesinin önceki akademik faaliyetlerinin listelendiği adımdır.
        """
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
        """
        Yürütücünün halihazırdaki projelerinin listelendiği adımdır.
        """
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
        """
        Projenin son haliyle kaydedildiği adımdır.
        """
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
            proje.tur_id = str(td['ProjeTurForm']['tur'])
        if 'ProjeCalisanlariForm' in td:
            proje.ProjeCalisanlari.clear()
            for calisan in td['ProjeCalisanlariForm']['Calisan']:
                proje.ProjeCalisanlari(ad=calisan['ad'], soyad=calisan['soyad'],
                                       nitelik=calisan['nitelik'],
                                       calismaya_katkisi=calisan['calismaya_katkisi'],
                                       kurum=calisan['kurum'])
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
                                tarih=datetime.now())
        proje.durum = 1
        if not proje.basvuru_rolu.exist:
            proje.basvuru_rolu = self.current.role
        proje.blocking_save()

    def proje_goster(self):
        """
        Proje başvurusunun öğretim üyesine özet halinde gösterildiği adımdır.
        """
        self.object = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.show()
        form = JsonForm()
        form.onay = fields.Button(_(u"Onaya Gönder"), cmd='onay')
        self.form_out(form)

    def onaya_gonder(self):
        """
        Projenin onaya gönderildiği adımdır.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.durum = 2
        proje.ProjeIslemGecmisi(eylem=_(u"Onaya Gönderildi"),
                                aciklama=_(u"Koordinasyon Birimine onaya gönderildi"),
                                tarih=datetime.now())
        proje.blocking_save()
        msg = {"title": _(u'Başvurunuzu tamamladınız!'),
               "body": _(u'Proje başvurunuz BAP birimine başarıyla iletilmiştir. '
                         u'Değerlendirme sürecinde size bilgi verilecektir.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

        role = Role.objects.get(user=self.current.user)
        wfi = WFInstance.objects.get(self.current.token)
        inv = TaskInvitation.objects.get_or_none(instance=wfi, role=role)
        if inv:
            title = inv.title
            inv.blocking_delete()
        else:
            title = "%s | %s" % (proje.proje_kodu, wfi.wf.title)
        self.current.task_data['INVITATION_TITLE'] = title

    def bildirim_gonder(self):
        """
        Koordinasyon biriminin kararı sonucu öğretim üyesine bildirim gönderilen adımdır.
        """
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
            help_text = _(
                u"%s adlı projeye daha sonra karar vermeyi seçtiniz. Başvuru Listeleme iş "
                u"akışından bu projeye ulaşabilirsiniz." % proje.ad)

        elif self.current.task_data['karar'] == 'onayla':
            role.send_notification(
                title=_(u"Proje Başvuru Durumu: %s" % proje.ad),
                message=_(
                    u"%s adlı proje başvurunuz koordinasyon birimi tarafından onaylanarak gündeme "
                    u"alınmıştır." % proje.ad),
                sender=self.current.user
            )
            karar = 'onayla'
            help_text = _(
                u"%s adlı projeyi onayladınız. Kararınızı değiştirmek istiyorsanız Başvuru "
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
        """
        Koordinasyon biriminin revizyon kararı sonrasında revizyon talebi mesajının öğretim üyesine
        gösterildiği adımdır.
        """
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        baslik = _(u"#### Revizyon Gerekçeleri:\n")
        msg = self.current.task_data['revizyon_gerekce']
        form = JsonForm(title=_(u"%s İsimli Proje İçin Revizyon Talebi" % proje.ad))
        form.help_text = baslik + msg
        form.devam = fields.Button(_(u"Revize Et"))
        self.form_out(form)
