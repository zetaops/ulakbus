# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import Okutman, Unit, AbstractRole
from zengine.views.crud import CrudView
from zengine.forms.json_form import JsonForm
from zengine.forms.fields import Integer, DateTime, Button, String
from zengine.models import BPMNWorkflow, Task
from zengine.lib.translation import gettext as _
from pyoko.exceptions import ObjectDoesNotExist

MESAJ = {
    'type': 'info', "title": _(u'İşlem Başarılı'),
    "msg": _(u'İlgili birime bağlı kişilere iş akışı aktarıldı.')
}


def format_date(start_date, finish_date):
    """

    Args:
        start_date: datetime (form input)
        finish_date: datetime (form input)

    Returns:
        start: string (02.10.2010)
        finish: string (10.10.2010)

    """
    start = datetime.strptime(start_date, '%d.%m.%Y')
    finish = datetime.strptime(finish_date, '%d.%m.%Y')
    return start, finish


class FormTask(JsonForm):
        tarih_baslangic = DateTime(_(u'Tarih Aralığı - Başlangıç'))
        tarih_bitis = DateTime(_(u'Tarih Aralığı - Bitis'))
        gonder = Button(_(u"Onayla"))


class FormTaskTypeA(FormTask):
    class Meta:
        include = ['abstract_role', 'unit', 'object_query_code', 'object_type', 'recursive_unit']


class FormTaskTypeB(FormTask):
    class Meta:
        include = ['abstract_role', 'get_roles_from', 'unit', 'object_query_code',
                   'object_type', 'recursive_unit']


class FormTaskTypeC(FormTask):
    class Meta:
        include = ['abstract_role', 'get_roles_from']


class FormTaskTypeD(FormTask):
    class Meta:
        include = ['abstract_role', 'get_roles_from', 'unit', 'recursive_unit']


class WorkflowManagement(CrudView):
    class Meta:
        model = 'BPMNWorkflow'

    """
        Oluşturulan workflowları, workflow'a göre uygun role sahip kişilere atama işlemi yapan workflowdur.
        Buradakı Bütün iş akışları sistem_yoneticisi_1 tarafından yapılır.
    """

    def wf_sec(self):
        _secim_wf = prepare_choices_for_model(BPMNWorkflow, programmable=True)
        _form = JsonForm(title=_(u"İş Yöneticisi"))
        _form.workflow = Integer(title=_(u"Workflow Seçiniz"), choices=_secim_wf)
        _form.gonder = Button(_(u"İlerle"))

    def wf_zamanla(self):
        workflow = self.input['form']['workflow']
        form = 'FormTaskType%s' % workflow.task_type
        _form = globals()[form]()

    def sistem_is_akisi_atama_form(self):
        """

            Sistem Yöneticisine iş akışı atanacak bölümüdür.
            Burada Sistem yöneticisi kendisinin yapması gereken iş akışını seçer.
            İş akışının yapılacağı başlangıç ve bitiş tarihi'ni seçerek iş akısını bitirir.

            Example:
                login: sistem_yoneticisi_1
                Workflow Seçiniz: guncel_donem_degistirme
                Tarih Aralığı - Başlangıç: 01.09.2016
                Tarih Aralığı - Bitiş: 08.09.2016
        """

        workflow = self.input['form']['workflow']
        baslangic_tarihi, bitis_tarihi = format_date(self.input['form']['tarih_baslangic'],
                                                     self.input['form']['tarih_bitis'])

        _secim_wf = prepare_choices_for_model(BPMNWorkflow, programmable=True)
        _form = JsonForm(title="Sistem Yöneticisi İş Akışı Atama")
        _form.workflow = Integer(title="Workflow Seçiniz", choices=_secim_wf)
        _form.tarih_baslangic = DateTime('Tarih Aralığı - Başlangıç')
        _form.tarih_bitis = DateTime('Tarih Aralığı - Bitis')
        _form.gonder = Button("Gönder")
        self.form_out(_form)

    def sistem_yon_kaydet(self):
        """
            Json Formun'da doldurulan bilgilere göre Task modeli doldurulur ve secilen is akışı
            Sistem Yöneticisi rolüne sahip kişilere gönderilir.

            Check User:
                Login: sistem_yoneticisi_1
        """
        baslangic_tarihi, bitis_tarihi = format_date(self.input['form']['tarih_baslangic'],
                                                     self.input['form']['tarih_bitis'])
        task = Task()
        task.wf = BPMNWorkflow.objects.get(self.input['form']['workflow'])
        task.abstract_role = AbstractRole.objects.get(name='Sistem Yöneticisi')
        task.name = task.wf.title
        task.start_date = baslangic_tarihi
        task.finish_date = bitis_tarihi
        task.run = True
        task.save()

        self.current.output['msgbox'] = MESAJ
    # sistem_is_akisi_atama -- finish -- #

    # oe_not_girisi_is_akisi_atama -- start -- #
    def not_girisi_is_akisi_atama_formu(self):
        """
            Öğretim Elemanı'na özel not girişi iş akışı atama formudur.
            Atanacak workflow bilindiği için sistem yöneticisinden workflow istenmez.
            Bunun yerine Okutmanın birimi, adı, soyadı, sınav türü, not girisinin yapılması gereken
            tarih aralıkları belirlenir.

            Examples:
                login: sistem_yoneticisi_1
                Birim Seçiniz: ULUSLARARASI İLİŞKİLER BÖLÜMÜ
                Sınav Türünü Seçiniz: Ara Sınav
                Okutman Adını Giriniz: İsmet
                Okutman Soyadını Giriniz: Tarhan
                Tarih Aralığı - Başlangıç: 10.10.2016
                Tarih Aralığı - Bitiş: 21.10.2016
        """

        _secim_unit = prepare_choices_for_model(Unit, unit_type="Bölüm")
        _form = JsonForm(title="Öğretim Elemanı Not Girişi İş Akışı Atama")
        _form.secim_unit = Integer(title="Birim Seçiniz", choices=_secim_unit)
        _form.sinav_turu = Integer("Sınav Türünü Seçiniz", choices="sinav_turleri")
        _form.okutman_ad = String('Okutman Adını Giriniz')
        _form.okutman_soyad = String('Okutman Soyadını Giriniz')
        _form.tarih_baslangic = DateTime('Tarih Aralığı - Başlangıç')
        _form.tarih_bitis = DateTime('Tarih Aralığı - Bitis')
        _form.gonder = Button("Gönder")
        self.form_out(_form)

    def ogretim_elemani_kontrol(self):
        """
            Form Ekranında yazılan ögretim elemanı adı ve soyadını kontrol eder.
            Eğer bu ad ve soyad a sahip öğretim elemanı varsa işlem devam eder.
            Yoksa tekrardan Form ekranına dönüş yapar.

        """
        try:
            self.current.task_data['okutman_key'] = Okutman.objects.get(
                ad=self.input['form']['okutman_ad'],
                soyad=self.input['form']['okutman_soyad']).key
        except ObjectDoesNotExist:
            msg = {
                'type': 'warn', "title": _(u'Böyle Bir Kayıt Yok'),
                "msg": _(u'İlgili Birime Ait Öğretim Elemanı Bulunamadı.')
            }
            self.current.output['msgbox'] = msg
            self.current.task_data['cmd'] = 'yok'

    def kaydet(self):
        """
            ogretim_elemani_kontrol ünde eğer ilgili ögretim elemanı varsa, bulunan öğretim elemanına
            not girişi iş akışı atama işlemi yapılır.

            Check User:
                Login: ogretim_uyesi_3
        """
        from pyoko.fields import DATE_FORMAT
        baslangic_tarihi, bitis_tarihi = format_date(self.input['form']['tarih_baslangic'],
                                                     self.input['form']['tarih_bitis'])
        bas_tarih = baslangic_tarihi.strftime(DATE_FORMAT)

        okutman = Okutman.objects.get(self.current.task_data['okutman_key'])
        role = okutman.personel.user.role_set[0].role
        task = Task()
        task.wf = BPMNWorkflow.objects.get(name='okutman_not_girisi')
        task.name = task.wf.title
        task.unit = Unit.objects.get(self.input['form']['secim_unit'])
        task.abstract_role = AbstractRole.objects.get(name='Öğretim Elemanı')
        task.role = role
        task.object_type = 'Sinav'
        task.object_query_code = {'okutman_id': self.current.task_data['okutman_key'],
                                  'tur': self.input['form']['sinav_turu'],
                                  'tarih__lt': bas_tarih}
        task.start_date = baslangic_tarihi
        task.finish_date = bitis_tarihi
        task.run = True
        task.save()

        self.current.output['msgbox'] = MESAJ

    # oe_not_girisi_is_akisi_atama -- finish -- #

    # workflow_management -- start -- #
    def is_akisi_atama_form(self):
        """
            Belli is akışlarını görevlendirmek üzere,
            ilgili bölüme ait role sahip kişi veya kişilere atanacak iş akışıdır.

            Examples:
                Login: sistem_yoneticisi_1
                Workflow Seçiniz: zaman_dilimi_duzenle
                Birim Seçiniz: ULUSLARARASI İLİŞKİLER BÖLÜMÜ
                Görevli Seçiniz: Ders Programı Koordinatörü
                Başlangıç Tarihi: 13.10.2016
                Bitiş Tarihi: 15.10.2016

        """
        _form = WorkflowJson(title="İş Akışı Atama")
        _form.tarih_baslangic = DateTime("Başlangıç Tarihi")
        _form.tarih_bitis = DateTime("Bitiş Tarihi")
        _form.gonder = Button("Gönder")
        self.form_out(_form)

    def kaydet_ve_gonder(self):
        """
            Secilen AbstractRole sahip kişilere atanmak üzere yeni bir task oluşturulup,
            Formdan gelen datalarla model doldurulur.

            Check User:
                Login: ders_programi_koordinatoru_1
        """
        workflow = self.input['form']['secim_workflow']
        unit = self.input['form']['secim_unit']
        gorev = self.input['form']['secim_gorev']
        baslangic_tarihi, bitis_tarihi = format_date(self.input['form']['tarih_baslangic'],
                                                     self.input['form']['tarih_bitis'])

        task = Task()
        task.wf = BPMNWorkflow.objects.get(workflow)
        task.name = task.wf.title
        task.unit = Unit.objects.get(key=unit)
        task.abstract_role = AbstractRole.objects.get(key=gorev)
        task.start_date = baslangic_tarihi
        task.finish_date = bitis_tarihi
        task.run = True
        task.save()

        self.current.output['msgbox'] = MESAJ
        # workflow_management -- finish -- #
