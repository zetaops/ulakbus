# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""
    İşten ayrılan personelin modelde arsiv alanı True yapılır.
    Modeldeki notlar alanı ile de işten ayrılan personel ile ilgili açıklama girme
    imkanı verilmiş olur.
"""
from pyoko import ListNode
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models import Personel, Role
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.models import WFInstance, TaskInvitation
from ulakbus.lib.view_helpers import prepare_choices_for_model


class IstenAyrilmaOnayForm(JsonForm):
    """
        Personel işten ayrılma işleminin onaylanması ve açıklama girilmesi
        amacıyla JsonForm class dan türetilmiş bir classdır.
    """

    class Meta:
        help_text = __(u"Personel İşten ayrılma işlemini onaylıyormusunuz?")
        title = __(u"Personel İşten Ayrılma")
        include = ["notlar"]

    devam_buton = fields.Button(__(u"Onayla"))
    iptal_buton = fields.Button(__(u"İptal"), flow='geri')


class WorkflowAtamaForm(JsonForm):
    class Meta:
        inline_edit = ['yeni_role']

        title = __(u"Kullanıcıya Ait Aktif Görevler")

    bitir_buton = fields.Button(__(u"Bitir"))

    class YeniRoller(ListNode):
        wf_name = fields.String(__(u"WF Adı"), readonly=True)
        eski_role = fields.String(__(u"Eski Rol"), readonly=True)
        yeni_role = fields.String(__(u"Yeni Rol"),
                                  choices=prepare_choices_for_model(Role),
                                  required=True)

    def generate_yeni_roller(self):
        """
            İşten ayrılacak personele ait rol veya roller getirilir. Bu roller de
            aktif iş akışı varmı diye bakılır varsa formda gösterilir.
            Aktif iş akışını atayacağı rolü seçerek, personelin işten ayrılması sağlanır.
        """
        user = Personel.objects.get(self.context.task_data["personel_id"]).user

        for rs in user.role_set:
            wf_instances = [ins.key for ins in WFInstance.objects.filter(
                current_actor=rs.role)]
            queryset = TaskInvitation.objects.filter(progress__in=[20, 30], role=rs.role)

            wf_names = list(set(q.wf_name for q in queryset.filter(instance_id__in=wf_instances)))
            for wf in wf_names:
                self.YeniRoller(
                    wf_name=wf,
                    eski_role=rs.role.name,
                )


class IstenAyrilma(CrudView):
    """
        Personel işten ayrılma wf adımlarının metodlarını içeren
        CrudView dan türetilmiş classdır.
    """

    class Meta:
        model = "Personel"

    def personel_id_kaydet(self):
        # Seçilmiş olan personelin id'si task data da saklanır
        self.current.task_data["personel_id"] = self.current.input["id"]

    def onay_form(self):
        # Onay form kullanıcıya gösteriliyor
        self.form_out(IstenAyrilmaOnayForm(self.object, current=self.current))

    def onayla(self):
        # Onaylanan işten ayrılma veritabanına işleniyor
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        # Burada personelin işten ayrıldığına dair bir açıklama metni girişi yapılmaktadır.
        personel.notlar = self.current.input["form"]["notlar"]
        personel.save()

    def wf_devir(self):
        """
            Aktif gorevlerin baska bir role atanacagi form ekrani
        """
        form = WorkflowAtamaForm(current=self.current)
        form.generate_yeni_roller()
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def wf_devir_onay(self):
        """
            Aktif iş akışlarını yeni seçilen role atama işlemi yapılır.
            İşlem tamamlandıktan sonra ilgili personelin rolü sistemden silinir.
        """
        yeni_roller = self.input['form']['YeniRoller']
        silinecek_roller = []
        if yeni_roller:
            for yr in yeni_roller:
                yeni_rol = Role.objects.get(yr['yeni_role'])
                eski_rol = Role.objects.get(name=yr['eski_role'])
                silinecek_roller.append(eski_rol)
                wf_name = yr['wf_name']
                instances = []

                for wfi in WFInstance.objects.filter(current_actor=eski_rol, name=wf_name):
                    wfi.current_actor = yeni_rol
                    wfi.blocking_save(query_dict={'current_actor': yeni_rol})
                    instances.append(wfi.key)

                for inv in TaskInvitation.objects.filter(progress__in=[20, 30],
                                                         role=eski_rol,
                                                         wf_name=wf_name,
                                                         instance_id__in=instances):
                    inv.role_id = yeni_rol.key
                    inv.blocking_save(query_dict={'role_id': yeni_rol.key})

        for r in silinecek_roller:
            r.blocking_delete()

        personel = Personel.objects.get(self.current.task_data["personel_id"])
        personel.arsiv = True
        personel.save()

    def iptal_islemi(self):
        form = JsonForm(title=_(u'İptal Edildi'))
        form.help_text = _(u"İşlemi iptal ettiniz. Ana sayfa'ya yönlendirileceksiniz")
        form.tamam_buton = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def anasayfa_yonlendirme(self):
        """
            Iptal isleminden sonra ana sayfa ekrani yuklenir.
        """
        self.current.output['cmd'] = 'reload'
