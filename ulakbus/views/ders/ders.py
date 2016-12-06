# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
"""Ders Modülü

İlgili İş Akışlarına ait sınıf ve metotları içeren modüldür.

Ders Ekle ve Ders Şubelendirme iş akışlarının yürütülmesini sağlar.

"""

from collections import OrderedDict
from pyoko import ListNode
from pyoko.db.adapter.db_riak import BlockSave, BlockDelete
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import AbstractRole, Role
from ulakbus.models.ogrenci import DegerlendirmeNot, OgrenciProgram
from ulakbus.models.ogrenci import Program, Okutman, Ders, Sube, Sinav, OgrenciDersi, Donem
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.lib.view_helpers import prepare_choices_for_model
from zengine.lib.translation import gettext as _, format_list, format_date


def okutman_choices():
    """Okutman Seçenekleri

    Returns:
        prepare_choices_for_model methodundan dönen değerleri dictionary
        formatında

    """

    return [{'name': name, 'value': value} for value, name in prepare_choices_for_model(Okutman)]


class ProgramBilgisiForm(forms.JsonForm):
    """
    ``DersEkle`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alana sahiptir.

    """

    class Meta:
        include = ['program']

    sec = fields.Button(_(u"Seç"), cmd="program_sec")


class DersBilgileriForm(forms.JsonForm):
    """
    ``DersEkle`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati',
                   'ects_kredisi',
                   'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci',
                   'ogrenme_ciktilari',
                   'ders_icerigi', 'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati',
                   'verilis_bicimi', 'donem',
                   'ders_koordinatoru']

    kaydet = fields.Button(_(u"Kaydet"), cmd="kaydet")


class DersDegerlendirmeForm(forms.JsonForm):
    class Meta:
        include = ['Degerlendirme']

    kaydet = fields.Button(_(u"Kaydet"), cmd="degerlendirme_kaydet", flow="end")
    kaydet_yeni_kayit = fields.Button(_(u"Kaydet/Yeni Kayıt Ekle"), cmd="kaydet", flow="start")


class DersEkle(CrudView):
    """Ders Ekle İş Akışı

    Ders Ekle, aşağıda tanımlı iş akışı adımlarını yürütür.

    - Program Formunu Listele
    - Program Seç
    - Ders Bilgilerini Gir
    - Kaydet
    - Kaydet/Yeni Kayıt Ekle

     Bu iş akışında kullanılan metotlar şu şekildedir:

     Program Formunu Listele:
        CrudView list metodu kullanılmıştır. Bu metot default olarak
        tanımlanmıştır. Program Bilgisi formunu listeler.

     Seç:
        Kayıtlı programlardan birini seçer.

     Ders Bilgilerini Gir:
        Ders Bilgileri formundaki alanlar doldurulur.

     Kaydet/Yeni Kayıt Ekle:
        Seçilen programı için  girilen ders bilgilerini kaydeder.
        Bu adımdan sonra iş akışı sona erer.

     Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model
     ``Ders`` modelidir. Meta.model bu amaçla kullanılmıştır.

     Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "Ders"

    def program_sec(self):
        """Program Seçimi"""

        self.set_form_data_to_object()
        self.current.task_data['program_id'] = self.object.program.key

    def degerlendirme_form(self):
        ders = Ders.objects.get(self.current.task_data['ders_id'])
        self.form_out(DersDegerlendirmeForm(ders, current=self.current))

    def kaydet(self):
        self.set_form_data_to_object()
        self.object.program = Program.objects.get(self.current.task_data['program_id'])
        self.save_object()
        self.current.task_data['ders_id'] = self.object.key
        # self.current.task_data['next'] = self.current.input['next']

    def ders_bilgileri(self):
        """Ders Bilgileri Formu"""

        self.form_out(DersBilgileriForm(self.object, current=self.current))

    def program_bilgisi(self):
        """Program Bilgisi Formu"""

        self.form_out(ProgramBilgisiForm(self.object, current=self.current))


class SecimForm(forms.JsonForm):
    """

    ``DersSubelendirme`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button(_(u"Seç"), cmd="ders_sec")


class ProgramForm(forms.JsonForm):
    """
    ``DersSubelendirme`` sınıfı için form olarak kullanılacaktır.

    """

    sec = fields.Button(_(u"Seç"), cmd="ders_sec")


class SubelendirmeForm(forms.JsonForm):
    """
    ``DersSubelendirme`` sınıfı için form olarak kullanılacaktır.
    """

    kaydet_ders = fields.Button(_(u"Kaydet ve Ders Seçim Ekranına Dön"), cmd="subelendirme_kaydet",
                                flow="ders_okutman_formu")
    program_sec = fields.Button(_(u"Kaydet ve Program Seçim Ekranına Dön"), cmd="subelendirme_kaydet",
                                flow="program_sec")
    bilgi_ver = fields.Button(_(u"Tamamla ve Hocaları Bilgilendir"), cmd="subelendirme_kaydet",
                              flow="bilgi_ver")

    class Subeler(ListNode):
        ad = fields.String(_(u'Şube Adı'))
        kontenjan = fields.Integer(_(u'Şube Kontenjanı'))
        dis_kontenjan = fields.Integer(_(u'Şube Dış Kontenjanı'))
        okutman = fields.String(_(u'Okutman'), choices=okutman_choices)


class NotGirisForm(forms.JsonForm):
    class Meta:
        inline_edit = ['degerlendirme', 'aciklama']

    class Ogrenciler(ListNode):
        ogrenci_no = fields.String(_(u'No'))
        ad_soyad = fields.String(_(u'Ad Soyad'))
        degerlendirme = fields.Integer(_(u'Not'))
        aciklama = fields.String(_(u'Açıklama'))
        key = fields.String(_(u'Key'), hidden=True)


class DersSubelendirme(CrudView):
    """Ders Şubelendirme İş Akışı

     Ders Şubelendirme, aşağıda tanımlı iş akışı adımlarını yürütür.

     - Program Formunu Listele
     - Program Seç
     - Ders Şubelendir
     - Şube Formunu Listele
     - Kaydet ve Ders Seçim Ekranına Dön
     - Kaydet ve Program Seçim Ekranına Dön
     - Tamamla ve Hocaları Bilgilendir

    Bu iş akışında kullanılan metotlar şu şekildedir:

    Program  Formunu Listele:
        CrudView list metodu kullanılmıştır.Bu metot default olarak
        tanımlanmıştır. Program formunu listeler.

    Seç:
        Kayıtlı programlardan birini seçer. Seçilen program kayıtlı
        dersleri döndürür.

    Şubelendir:
        Şubelendirelecek ders seçilir.

    Şube Formunu Listele:
        Şubelenmiş dersin şube detaylarını gösterir, seçilen dersi
        şubelendirir.

    Kaydet ve Ders Seçim Ekranına Dön:
        Şubelendirilmiş dersi kaydeder ve ders seçim ekranından geri
        döner. İş akışına ders seçim ekranından devam eder.

    Kaydet ve Program Seçim Ekranına Dön:
        Şubelendirilmiş dersi kaydeder ve program seçim  ekranına geri
        döner. İş akışı Program formundan devam eder.

    Tamamla ve Hocaları Bilgilendir:
         Şubelendirilmiş dersin hocalarına, şube ve ders bilgileri
         aktarılır. Bu adımdan sonra iş akışı sona eriyor.

    Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model
    ``Sube`` modelidir. Meta.model bu amaçla kullanılmıştır.

    Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = "Sube"

    def program_sec(self):
        """Program Seçim Adımı

        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.

        """

        _form = ProgramForm(title=_(u"Program Seçiniz."), current=self.current)
        choices = prepare_choices_for_model(Program, yoksis_no=self.current.role.unit.yoksis_no)
        _form.program = fields.Integer(choices=choices)
        self.form_out(_form)

    def ders_sec(self):
        """Ders Seç Adımı

        Seçilen programa bağlı dersler, eğer daha önce şubelendirme
        yapıldıysa şube listesiyle birlikte ekrana getirilir.

        Formun herbir satırı ders ve şubeleri ile birlikte, ilgili
        ders için şubelendirme formuna bağlı bir butondan oluşur.

        Şubelendirme butonunun ``object_key`` i ``sube`` olarak
        tanımlanmıştır. Sonraki adımda bu key yardımıyla şube formu,
        ekrana getirilir. ``ders_okutman_formu`` metodu içinde şu
        şekilde kullanılmıştır::

            ders = Ders.objects.get(key=self.current.input['sube'])

        """

        self.set_client_cmd('form')
        self.output['objects'] = [[_(u'Dersler')], ]
        if 'program' in self.current.input['form']:
            self.current.task_data['program'] = self.current.input['form']['program']
        dersler = Ders.objects.filter(program_id=self.current.task_data['program'])
        for d in dersler:
            ders = "%s - %s (%s ECTS)" % (d.kod, d.ad, d.ects_kredisi)
            ders_subeleri = Sube.objects.filter(ders=d)
            subeler = []

            def sube_append(sube):
                    subeler.append(
                        {
                            "sube_ad": sube.ad,
                            "okutman_ad": sube.okutman.ad,
                            "okutman_soyad": sube.okutman.soyad,
                            "okutman_unvan": sube.okutman.okutman.get_unvan_display(),
                            "kontenjan": sube.kontenjan,
                        }
                    )

            for sube in ders_subeleri:
                sube_append(sube)

            ders_subeleri = [_(u"""* **%(unvan)s %(ad)s %(soyad)s**
                                Sube: %(sube)s - Kontenjan: %(kontenjan)s""") % {
            'unvan': sb['okutman_unvan'], 'ad': sb['okutman_ad'],
            'soyad': sb['okutman_soyad'], 'sube': sb['sube_ad'],
            'kontenjan': sb['kontenjan']} for sb in subeler]
            item = {
                "fields": ["%s\n%s" % (ders, "\n".join(ders_subeleri)), ],
                "actions": [
                    {'name': _(u'Şubelendir'), 'cmd': 'ders_okutman_formu', 'show_as': 'button',
                     'object_key': 'sube'},
                ],
                "key": d.key
            }
            self.output['objects'].append(item)

    def ders_okutman_formu(self):
        """Ders Okutman Formu

        Şubelendirme için seçilen dersin, şube bilgileri formunu oluşturur.

        """

        # subelendirme icin secilen dersi getir
        ders = Ders.objects.get(key=self.current.input['sube'])
        # sonraki adimlar icin task data icine koy
        self.current.task_data['ders_key'] = ders.key

        # formu olusturmaya basla
        subelendirme_form = SubelendirmeForm(
            current=self.current,
            title=_(u'%(donem)s / %(ders)s dersi için şubelendirme') % {'donem': ders.donem, 'ders': ders},
        )
        # formun sube listesini olustur
        subeler = Sube.objects.filter(ders=ders)
        for sube in subeler:
            subelendirme_form.Subeler(ad=sube.ad, kontenjan=sube.kontenjan,
                                      dis_kontenjan=sube.dis_kontenjan,
                                      okutman=sube.okutman.key)

        self.form_out(subelendirme_form)

    def subelendirme_kaydet(self):
        """Şubelendirme Kaydet

        Şubelendirme formundan gelen dataları kaydeder.

        """

        sb = self.input['form']['Subeler']
        ders = self.current.task_data['ders_key']
        mevcut_subeler = Sube.objects.filter(ders_id=ders)
        with BlockSave(Sube):
            for s in sb:
                okutman = s['okutman']
                kontenjan = s['kontenjan']
                ad = s['ad']
                dis_kontenjan = s['dis_kontenjan']
                donem = Donem.guncel_donem(self.current)
                sube, is_new = Sube.objects.get_or_create(okutman_id=okutman, ders_id=ders,
                                                          kontenjan=kontenjan, ad=ad, dis_kontenjan=dis_kontenjan,
                                                          donem=donem)
                # mevcut_subelerden cikar
                mevcut_subeler = list(set(mevcut_subeler) - {sube})
                if is_new:
                    self.bilgilendirme_mesaji_yolla(sube)
                else:
                    self.current.task_data['yeni_okutmanlar'] = []
        # çıkarılan şube
        with BlockDelete(Sube):
            for s in mevcut_subeler:
                self.bilgilendirme_mesaji_yolla(s)
                s.delete()

    def bilgilendirme_mesaji_yolla(self,sube):
        title = _(u"Şubelendirme")
        bolum_baskani = "%s %s" % (self.current.user.name, self.current.user.surname)
        msg = _(u"Bölüm Başkanı %s tarafından şubelerinizde değişiklikler yapılmıştır.") % bolum_baskani
        self.current.task_data['yeni_okutmanlar'] = []
        abstract_role = AbstractRole.objects.get("OGRETIM_ELEMANI")
        okutman = sube.okutman
        self.current.task_data['yeni_okutmanlar'].append(okutman.__unicode__())
        user = okutman.personel.user if okutman.personel else okutman.harici_okutman
        try:
            birim = Program.objects.get(self.current.task_data['program']).birim
            role = Role.objects.get(abstract_role=abstract_role, user=user, unit=birim)
            role.send_notification(title=title, message=msg, sender=self.current.user)
        except ObjectDoesNotExist:
            pass


    def bilgi_ver(self):
        """Bilgi ver

        Şubelendirme bilgileri ilgili okutmanlara iletilir.

        """
        if self.current.task_data['yeni_okutmanlar']:
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'Mesaj İletildi'),
                "msg": _(u'Şubelendirme bilgileri şu hocalara iletildi: %s') % format_list(
                    self.current.task_data['yeni_okutmanlar'])}
        else:
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'Mesaj İletildi'),
                "msg": _(u'Derse ait şubelerde değişiklik yapmadınız.')}


class NotGirisi(CrudView):
    """Okutman Not Girişi

    Okutmanların Sınavlara ait öğrenci notlarını sisteme girebilmesini
    sağlayan workflowa ait metdodları barındıran sınıftır.

    """

    class Meta:
        model = "DegerlendirmeNot"

    def ders_secim(self):
        """Not Girişi Ders Seçimi

        Okutmanın kendisine ait şubelerin listelendiği seçim adımına
        ait olan metot.

        Bu method seçilen şubeyi bir sonraki workflow adımı olan ve
        ``sinav_sec`` methodu ile elde edilen sınav seçim adımına
        aktarmaktadır.

        """

        _form = forms.JsonForm(current=self.current, title=_(u"Ders Seçim Formu"))
        user = self.current.user
        subeler = Sube.objects.filter(okutman_id=self.get_okutman_key)
        _form.sube = fields.Integer(_(u"Şube Seçiniz"),
                                    choices=prepare_choices_for_model(Sube,
                                                                      okutman_id=self.get_okutman_key))
        _form.sec = fields.Button(_(u"Seç"), cmd=_(u"Ders Şubesi Seçin"))
        self.form_out(_form)

    def sinav_sec(self):
        """Not Girişi Sınav Seç

        Okutmanın, seçilen şubeye ait sınavları görebildiği ve sınav
        seçimi yapabildiği adıma ait olan method.

        Seçilen şube, ``ders_secim`` methodu içinde tanımlanmış olan
        ``JsonForm`` tarafından iletilmekte ve bu method içerisinde
        aşağıdaki şekilde elde edilmektedir::

            sube_key = self.current.input['form']['sube']

        Sinavlar, bir önceki şube seçim adımında seçilmiş olan şubeye
        ait olacak şekilde filtrelenmektedir::

            _form.sinav=fields.Integer("Sınav Seçiniz",
              choices=prepare_choices_for_model(Sinav, sube_id=sube_key))

        """

        _form = forms.JsonForm(current=self.current, title=_(u"Sınav Seçim Formu"))

        try:
            sube_key = self.current.input['form']['sube']
        except:
            sube_key = self.current.task_data["sube"]

        _form.sinav = fields.Integer(_(u"Sınav Seçiniz"),
                                     choices=prepare_choices_for_model(Sinav, sube_id=sube_key))
        self.current.task_data["sube"] = sube_key
        _form.sec = fields.Button(_(u"Seç"), cmd=_(u"Sınav Seçin"))
        self.form_out(_form)

    def sinav_kontrol(self):
        """Seçilen sınava ait notların onaylanmış (teslim edilmiş) olup
        olmadığını kontrol eden method.

        Bu method ile task_data içerisine seçili sınavın onay durumu
        aşağıdaki şekilde tanımlanmaktadır::

            self.current.task_data['sinav_degerlendirme'] = sinav.degerlendirme

        Bu tanımlama ile, BMPN dosyası üzerinde tanımladığmız XOR kapısı
        sayesinde notları onaylanmış (teslim edilmiş) sınavlara ait
        notlar bir önizleme ekranında görüntülenrek, tekrar işlenmesi
        ve değiştirilmesi engellenmektedir.

        """

        sinav_key = self.current.input['form']['sinav']
        self.current.task_data['sinav_key'] = sinav_key
        sinav = Sinav.objects.get(sinav_key)
        self.current.task_data['sinav_degerlendirme'] = sinav.degerlendirme

    def not_girisi(self):
        """Seçilen sınava ait notların sisteme girilmesini sağlayan method.
        Bu method hem ``sinav_kontrol`` hem de ``not_kontrol`` methodu
        üzerinden gelen yönlendirmeleri karşılamaktadır.

        ``not_kontrol`` methodu (not kontrol adımı), okutmanın girdiği
        notları değiştirme ihtiyacı göz önünde bulundurularak
        geliştirilmiştir.

        Not kontrol adımı üzerinden gelen yönlendirmelerde güncel not
        verisini elde edebilmek için ``task_data`` altında notlar
        tanımına bakılmaktadır. Bu tanım ``not_kontrol`` methodu
        içerisinde yapıldığı, için bu veriyi barındıran bütün
        yönlendirmelerin bu adımdan yapıldığı bilinmektedir.

        Bu tanımın bulunmadığı yönlendirmelerde ise, notlar
        veritabanı üzerinden sorgulanarak listelenmektedir.

        Bu methodun barındırdığı ``NotGirisForm`` adlı form ise
        ``not_form_inline_edit`` adlı form modifier ile
        ``degerlendirme`` ve ``aciklama`` alanlarına inline edit
        özelliği kazandırılmaktadır.

        """

        _form = NotGirisForm(current=self.current, title=_(u"Not Giriş Formu"))
        sinav_key = self.current.task_data['sinav_key']
        sube_key = self.current.task_data["sube"]
        sinav = Sinav.objects.get(sinav_key)

        try:
            ogrenciler = self.current.task_data["notlar"]
            for ogr in ogrenciler:
                _form.Ogrenciler(ad_soyad='%s' % (ogr['ad_soyad']),
                                 ogrenci_no=ogr['ogrenci_no'], degerlendirme=ogr['degerlendirme'],
                                 aciklama=ogr['aciklama'],
                                 key=ogr['key'])
        except:
            ogrenciler = OgrenciDersi.objects.filter(sube_id=sube_key)

            for ogr in ogrenciler:
                try:  # Öğrencinin bu sınava ait daha önceden kayıtlı notu var mı?
                    degerlendirme = DegerlendirmeNot.objects.get(sinav=sinav,
                                                                 ogrenci=ogr.ogrenci_program.ogrenci)
                    puan = degerlendirme.puan
                    aciklama = degerlendirme.aciklama
                    degerlendirme_key = degerlendirme.key
                except:
                    puan = 0
                    aciklama = ""
                    degerlendirme_key = ""

                _form.Ogrenciler(ad_soyad='%s %s' % (
                ogr.ogrenci_program.ogrenci.ad, ogr.ogrenci_program.ogrenci.soyad),
                                 ogrenci_no=ogr.ogrenci_program.ogrenci_no, degerlendirme=puan,
                                 aciklama=aciklama,
                                 key=degerlendirme_key)

        _form.kaydet = fields.Button(_(u"Önizleme"), cmd="not_kontrol")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def not_kontrol(self):
        """Okutmanların girmiş olduğu öğrenci notlarının listelenmesini
        sağlayan method.

        Bu method hem ``sinav_kontrol`` methodu hem de ``not_girisi``
        methodları üzerinden yapılan yönlendirmeleri karşılar. Eğer
        seçilen sınava ait notlar onaylanmış (teslim edilmiş) ise
        ``not_giris`` methoduna başlı olan not giriş adımı atlanarak bu
        adıma yönlendirme yapılmaktadır. Bu durumda notlar, veritabanı
        üzerinden alınarak listelenirken, ``not_girisi`` adımından gelen
        yönlendirmelerde form ile birlikte gönderilen veriler
        listelenmektedir.

        ``sinav_kontrol`` methodu ile yapılan yönlendirmelerde notlar
        üzerinde herhangi bir güncelleme, değişiklik yapılamayacağı için
        bu operasyonlara ait form düğmeleri gösterilmemekte ve okutmana
        bu dersler üzerinde bir değişiklik yapamayacağını bildiren bir
        mesaj kutusu gösterilmektedir.

        """

        _form = forms.JsonForm(current=self.current, title=_(u"Not Önizleme Ekranı"))

        try:  # Eğer istek sinav_kontrol aşamasından yönlendirilmemişse öğrenci notları için formdan gelen veriyi kullan
            ogrenci_notlar = self.current.input['form']['Ogrenciler']
            self.current.task_data["notlar"] = ogrenci_notlar

            notlar = []
            for ogr in ogrenci_notlar:
                ogrnot = OrderedDict({})
                ogrnot[_(u'Öğrenci No')] = ogr['ogrenci_no']
                ogrnot[_(u'Adı Soyadı')] = ogr['ad_soyad']
                ogrnot[_(u'Değerlendirme')] = ogr['degerlendirme']
                ogrnot[_(u'Açıklama')] = ogr['aciklama']
                notlar.append(ogrnot)

        except:  # Eğer istek sinav_kontrol aşamasından yönlendirilmişse notlar için veritabanı kayıtlarını kullan
            sinav_key = self.current.task_data['sinav_key']
            sube_key = self.current.task_data["sube"]
            sinav = Sinav.objects.get(sinav_key)
            ogrenciler = OgrenciDersi.objects.filter(sube_id=sube_key)
            notlar = []

            for ogr in ogrenciler:
                try:  # Öğrencinin bu sınava ait daha önceden kayıtlı notu var mı?
                    degerlendirme = DegerlendirmeNot.objects.get(sinav=sinav,
                                                                 ogrenci=ogr.ogrenci_program.ogrenci)
                    puan = degerlendirme.puan
                    aciklama = degerlendirme.aciklama
                except:
                    puan = 0
                    aciklama = ""

                ogrnot = OrderedDict({})
                ogrnot[_(u'Öğrenci No')] = ogr.ogrenci_program.ogrenci_no
                ogrnot[_(u'Adı Soyadı')] = '%s %s' % (
                ogr.ogrenci_program.ogrenci.ad, ogr.ogrenci_program.ogrenci.soyad)
                ogrnot[_(u'Değerlendirme')] = puan
                ogrnot[_(u'Açıklama')] = aciklama
                notlar.append(ogrnot)

        # Eğer notlar okutman tarından onaylanmışsa (teslim edilmişse) uyarı göster
        if self.current.task_data['sinav_degerlendirme']:
            self.current.output['msgbox'] = {

                'type': 'info', "title": _(u'Notlar Onaylandı'),
                "msg": _(u'Bu derse ait notlar onaylanmış olduğu için içeriği değiştirilemez.')

            }
            _form.ders_secim = fields.Button(_(u"Ders Seçim Ekranına Dön"), cmd="ders_sec",
                                             flow="ders_secim_adimina_don")
            _form.sinav_secim = fields.Button(_(u"Sınav Seçim Ekranına Dön"), cmd="sinav_sec",
                                              flow="sinav_secim_adimina_don")

        else:  # Eğer notlar hala onaylanmamışsa (teslim edilmemişse) form düğmelerini göster

            _form.not_onay = fields.Boolean(_(u"Sınav Notlarını Onaylıyorum (Bu işlem geri alınamaz!)"))
            _form.not_duzenle = fields.Button(_(u"Notları Düzenle"), cmd="not_girisi",
                                              flow="not_giris_formuna_don")
            _form.kaydet = fields.Button(_(u"Kaydet"), cmd="not_kaydet", flow="end")
            _form.kaydet_ve_ders_sec = fields.Button(_(u"Kaydet ve Ders Seçim Ekranına Dön"),
                                                     cmd="ders_sec",
                                                     flow="ders_adimina_don")
            _form.kaydet_ve_sinav_sec = fields.Button(_(u"Kaydet ve Sınav Seçim Ekranına Dön"),
                                                      cmd="sinav_sec",
                                                      flow="sinav_adimina_don")

        self.current.output['object'] = {
            "type": "table-multiRow",
            "fields": notlar,
            "actions": False
        }
        self.form_out(_form)

    def not_kaydet(self):
        """Okutmanın girmiş olduğu notların veritabanına kaydedilmesini
        sağlayan method.

        Bu method, önceden girilmiş olan notları veritabanı üzerinde
        güncellerken, key verisi olmayan not girişleri için veritabanı
        üzerinde yeni bir kayıt açmaktadır.

        """

        term = Donem.guncel_donem(self.current)
        sinav_key = self.current.task_data["sinav_key"]
        sube_key = self.current.task_data["sube"]

        sinav = Sinav.objects.get(sinav_key)
        ders = sinav.ders

        for ogrenci_not in self.current.task_data["notlar"]:

            try:
                ogr_data = OgrenciProgram.objects.get(ogrenci_no=ogrenci_not['ogrenci_no'])

                if ogrenci_not['key']:  # Önceden girilmiş bir kayıt mı?
                    ogr_not = DegerlendirmeNot.objects.get(ogrenci_not['key'])
                else:
                    ogr_not = DegerlendirmeNot()

                ogr_not.puan = ogrenci_not['degerlendirme']
                ogr_not.aciklama = ogrenci_not['aciklama']
                ogr_not.ogrenci_no = ogrenci_not['ogrenci_no']
                ogr_not.donem = '%s' % term.ad
                ogr_not.yil = term.baslangic_tarihi.year
                ogr_not.ogretim_elemani = self.get_okutman_name_surname
                ogr_not.ders = ders
                ogr_not.sinav = sinav
                ogr_not.ogrenci = ogr_data.ogrenci
                ogr_not.sinav_tarihi = sinav.tarih
                ogr_not.save()

            except:
                pass

        # Okutman notları onayladığını (teslim ettiğini) bildirmişse

        if self.current.input['form']['not_onay']:
            sinav.degerlendirme = True
            sinav.save()

    def kayit_bilgisi_ver(self):
        sinav_key = self.current.task_data["sinav_key"]
        sinav = Sinav.objects.get(sinav_key)
        sinav_tarihi = format_date(sinav.tarih)

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Notlar Kaydedildi'),
            "msg": _(u'%(ders)s dersine ait %(tarih)s tarihli sınav notları kaydedildi') % {
            'ders': sinav.ders.ad, 'tarih': sinav_tarihi}}

    @property
    def get_okutman_key(self):
        """Harici okutman ve okutman kayıt key'lerinin ayrımını sağlayan method.
        """
        return self.current.user.personel.okutman.key if self.current.user.personel.key else self.current.user.harici_okutman.okutman.key

    @property
    def get_okutman_name_surname(self):
        """Harici okutman ve okutman ad,soyad ayrımını sağlayan method.
        """
        return "%s %s" % (self.current.user.personel.okutman.ad,
                          self.current.user.personel.okutman.soyad) if self.current.user.personel.key else "%s %s" % (
            self.current.user.harici_okutman.ad, self.current.user.harici_okutman.soyad)
