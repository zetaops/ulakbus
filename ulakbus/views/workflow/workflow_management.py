# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime
from ulakbus.lib.view_helpers import prepare_choices_for_model
from zengine.views.crud import CrudView
from zengine.forms import JsonForm
from zengine.forms.fields import Integer, Button
from zengine.models import BPMNWorkflow, Task
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.models import AbstractRole, Role, Unit


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
    class Meta:
        include = ['abstract_role', 'start_date', 'finish_date']

    gonder = Button(__(u"Onayla"))
    geri = Button(__(u"Geri"), cmd='geri')


form_include_A = ['unit', 'object_query_code', 'object_type', 'recursive_units']
form_include_B = ['get_roles_from', 'unit', 'object_query_code', 'object_type', 'recursive_units']
form_include_C = ['get_roles_from']
form_include_D = ['get_roles_from', 'unit', 'recursive_units']

help_text_A = __(
u"""Modelin seçildiği, role özel atanan iş akışı atama formu:
* Model tipi seçilmesi zorunludur.
* Soyut rol secilmesi zorunludur.
* Arama sorgusu yazılması zorunludur ve "role" ile başlamalıdır.
Örnek: Şube modelini kullanan bir iş akışının okutmanlara özel gitmesi için sorgunun;
okutman=role.user.personel.okutman şeklinde olmalıdır.
* Birim seçilmesi zorunludur. Eğer seçilen birim Fakülte ise
alt birimlerde ki rolleri getir seçeneği işaretlenmesi zorunludur.
* İş akışının başlangıç ve bitiş zamanlari girilmesi zorunludur.
""")

help_text_B = __(
u"""Modelin seçildiği, aynı soyut role sahip kişilere aynı iş akışı atama formu:
* Model tipi seçilmesi zorunludur.
* Arama sorgusu yapılması zorunlu değildir.
Eğer bir sorgu yapılacak ise sorgu kodu "role" ile başlamamalıdır.
Örnek: personel modelini kullanan bir iş akışı için sorgu şu şekilde olabilir; personel_turu=2
* Eğer rolleri getir secenegi kullanılırsa, birim ile soyut rol kullanılmaz.
Bu tam tersi durum içinde geçerlidir.
* İş akışının başlangıç ve bitiş zamanlari girilmesi zorunludur.

""")
help_text_C = __(
u"""Modelin olmadığı, aynı soyut role sahip kişilere aynı iş akışı atama formu:
* Burada iki seçenek vardır. Ya rolleri getir secenegi kullanılır ya da soyut rol seçeneği.
""")
help_text_D = __(
u"""Modelin olmadığı aynı soyut role sahip, role özel atanan iş akışı atama formu:
 * Birim secilirse, soyut rol seceneğininde secilmezi zorunludur.
 Eğer birim fakülte ise alt birimlerde ki rolleri getir seçeneğinin de seçilmesi zorunludur.
 get_roles_from seçenegi boş bırakılır.
 * rolleri getir seçeneği seçilirse, diger seçenekler boş bırakılır
""")


class WorkflowManagement(CrudView):
    class Meta:
        model = 'Task'

    def wf_sec(self):
        _secim_wf = prepare_choices_for_model(BPMNWorkflow, programmable=True)
        _form = JsonForm(title=_(u"İş Yöneticisi"))
        _form.workflow = Integer(title=_(u"Workflow Seçiniz"), choices=_secim_wf)
        _form.gonder = Button(_(u"İlerle"))

        self.form_out(_form)

    def wf_zamanla(self):
        self.current.task_data['wf_name'] = self.input['form']['workflow']
        workflow = BPMNWorkflow.objects.get(name=self.current.task_data['wf_name'])
        include_fields = 'form_include_%s' % workflow.task_type
        help_text = 'help_text_%s' % workflow.task_type
        _form = FormTask(self.object, current=self.current)
        _form.Meta.include.extend(globals()[include_fields])
        _form.title = workflow.title
        _form.help_text = globals()[help_text]
        self.form_out(_form)

    def bilgi_ekrani(self):
        wf = BPMNWorkflow.objects.get(name=self.current.task_data['wf_name'])

        self.set_form_data_to_object()
        self.object.wf = wf
        self.object.name = wf.title or wf.name
        self.object.run = True
        self.save_object()

        self.current.output['msgbox'] = {"type": _(u"info"),
                                         "title": _(u"İşlem Başarılı"),
                                         "msg": _(u"İş akışı ilgili rollere aktarıldı.")}
