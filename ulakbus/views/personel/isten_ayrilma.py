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
from ulakbus.models import Personel, Role, HitapSebep
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine.models import WFInstance, TaskInvitation
from ulakbus.lib.view_helpers import prepare_choices_for_model
from datetime import datetime


class OncekiIstenAyrilmalari(JsonForm):

    class Meta:
        title = __(u"Personel İşten Ayrılma")

    class IstenAyrilmaBilgileri(ListNode):
        class Meta:
            title = __(u"Personele Ait Silinmis Kayit Bilgileri")
        ayrilma_sebeb = fields.String(__(u"Ayrılma Sebebi"), readonly=True)
        ayrilma_tarih = fields.String(__(u"Ayrılma Tarihi"), readonly=True)
        ayrilma_not = fields.String(__(u"Ayrılma Notu"), readonly=True)

    def ayrilma_bilgilerini_doldur(self):
        personel = Personel.objects.get(self.context.task_data['personel_id'])

        if personel.IstenAyrilma:
            for ia in personel.IstenAyrilma:
                self.IstenAyrilmaBilgileri(ayrilma_sebeb=ia.gorevden_ayrilma_sebep.ad,
                                           ayrilma_tarih=ia.gorevden_ayrilma_tarihi,
                                           ayrilma_not=ia.gorevden_ayrilma_not)
        else:
            self.help_text = __(u"Personele ait silinmiş kayıt bulunmamaktadır.")

    isten_ayril = fields.Button(__(u"İşten Ayrıl"), style='btn-primary')


class IstenAyrilmaOnayForm(JsonForm):
    """
        Personel işten ayrılma işleminin onaylanması ve açıklama girilmesi
        amacıyla JsonForm class dan türetilmiş bir classdır.
    """

    class Meta:
        help_text = __(u"Personel işten ayrılma formu")
        title = __(u"Personel İşten Ayrılma")

    ayrilma_sebeb = fields.Integer(__(u"Ayrılma Sebebi"),required=True)
    ayrilma_tarih = fields.Date(__(u"Ayrılma Tarihi"), required=True)
    ayrilma_not = fields.Text(__(u"Ayrılma Notu"), required=False)

    devam_buton = fields.Button(__(u"Devam"), style='btn-primary')


class WorkflowAtamaForm(JsonForm):
    class Meta:
        inline_edit = ['yeni_role']

        title = __(u"Kullanıcıya Ait Aktif Görevler")

    bitir_buton = fields.Button(__(u"Bitir"), style='btn-success')

    class YeniRoller(ListNode):
        wf_name = fields.String(__(u"WF Adı"), readonly=True)
        eski_role = fields.String(__(u"Eski Rol"), readonly=True)
        yeni_role = fields.String(__(u"Yeni Rol"), required=True)
        # TODO:yeni_role = fields.String(__(u"Yeni Rol"), choices=prepare_choices_for_model(Role),required=True)
        # TODO: Pyoko da implement edilen threaded yapıda problem çıkardığı için choices kaldırıldı. Çözüm aranacak.

    def generate_yeni_roller(self):
        """
            İşten ayrılacak personele ait rol veya roller getirilir. Bu roller de
            aktif iş akışı varmı diye bakılır varsa formda gösterilir.
            Aktif iş akışını atayacağı rolü seçerek, personelin işten ayrılması sağlanır.
        """
        user = Personel.objects.get(self.context.task_data["personel_id"]).user

        for rs in user.role_set:
            wf_instances = [ins.key for ins in WFInstance.objects.order_by().filter(current_actor=rs.role)]
            queryset = TaskInvitation.objects.order_by().filter(progress__in=[20, 30], role=rs.role)
            if queryset:
                wf_names = list(set(q.wf_name for q in queryset.order_by().filter(
                    instance_id__in=wf_instances)))
                for wf in wf_names:
                    self.YeniRoller(
                        wf_name=wf,
                        eski_role=rs.role.name,
                    )
            else:
                self.context.task_data['gorev_yok'] = "Kullaniciya ait aktif gorev bulunmamaktadir."


class IstenAyrilma(CrudView):
    """
        Personel işten ayrılma wf adımlarının metodlarını içeren
        CrudView dan türetilmiş classdır.
    """
    # Engelli personel sayısı toplam personel sayısının %3 nün altına düşemez.
    # engelli_personel_katsayisi değişkeni bunu ifade eder.
    engelli_personel_katsayisi = 0.03

    class Meta:
        model = "Personel"

    def personel_id_kaydet(self):
        # Seçilmiş olan personelin id'si task data da saklanır
        self.current.task_data["personel_id"] = self.current.input["id"]

    def list(self, custom_form=None):
        custom_form = OncekiIstenAyrilmalari(current=self.current)
        custom_form.ayrilma_bilgilerini_doldur()
        self.form_out(custom_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_selection"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def isten_ayrilma_form(self):
        # Onay form kullanıcıya gösteriliyor
        form = IstenAyrilmaOnayForm(current=self.current)
        form.set_choices_of('ayrilma_sebeb',choices = prepare_choices_for_model(HitapSebep))
        self.form_out(form)

    def kontrol(self):
        self.current.task_data['gorevden_ayrilma_sebep_id'] = \
            self.current.input["form"]["ayrilma_sebeb"]
        self.current.task_data['gorevden_ayrilma_tarihi'] = \
            self.current.input["form"]["ayrilma_tarih"]
        self.current.task_data['gorevden_ayrilma_not'] = self.current.input["form"]["ayrilma_not"]

        personel = Personel.objects.get(self.current.task_data["personel_id"])
        gorevden_ayrilma_tarihi = datetime.strptime(
            self.current.input["form"]["ayrilma_tarih"], "%d.%m.%Y").date()

        self.engelli_personel_kontrol(personel=personel)
        if personel.mecburi_hizmet_suresi:
            self.zorunlu_hizmet_kontrolu(ayrilma_tarihi=gorevden_ayrilma_tarihi,
                                         mecburi_gorev_tarihi=personel.mecburi_hizmet_suresi)

    def onay_form(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        if 'uyari_mesaji' in self.current.task_data:
            msg = self.current.task_data['uyari_mesaji']
        else:
            msg = 'Bu personeli silmek istiyor musunuz ?'

        title = "%s %s personelini silme işlemi" % (personel.ad, personel.soyad)

        form = JsonForm()
        form.title = _(u"%(title)s") % {'title': title}
        form.help_text = _(u"%(msg)s") % {'msg': msg}
        form.evet = fields.Button(_(u"Sil"), style='btn-warning')
        form.hayir = fields.Button(_(u"İptal"), style='btn-info', flow='iptal')
        self.form_out(form)

    def onayla(self):
        # Onaylanan işten ayrılma veritabanına işleniyor
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        # Burada personelin işten ayrıldığına dair bir açıklama metni girişi yapılmaktadır.
        sebep_id = self.current.task_data['gorevden_ayrilma_sebep_id']
        personel.IstenAyrilma(
            gorevden_ayrilma_sebep=HitapSebep.objects.get(sebep_id),
            gorevden_ayrilma_tarihi=self.current.task_data['gorevden_ayrilma_tarihi'],
            gorevden_ayrilma_not=self.current.task_data['gorevden_ayrilma_not']
        )
        personel.kadro.durum = 2
        personel.kadro.save()
        personel.save()

    def wf_devir(self):
        """
            Aktif gorevlerin baska bir role atanacagi form ekrani
        """
        form = WorkflowAtamaForm(current=self.current)
        form.generate_yeni_roller()
        if 'gorev_yok' in self.current.task_data:
            form.help_text = self.current.task_data['gorev_yok']
            form.title = ''
            form.exclude = ['YeniRoller']

        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def wf_devir_onay(self):
        """
            Aktif iş akışlarını yeni seçilen role atama işlemi yapılır.
            İşlem tamamlandıktan sonra ilgili personelin rolü sistemden silinir.
        """
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        silinecek_roller = []
        if 'YeniRoller' in self.input['form'] and self.input['form']['YeniRoller']:
            yeni_roller = self.input['form']['YeniRoller']
            for yr in yeni_roller:
                yeni_rol = Role.objects.get(yr['yeni_role'])
                eski_rol = Role.objects.get(name=yr['eski_role'])
                silinecek_roller.append(eski_rol)
                wf_name = yr['wf_name']
                instances = []

                for wfi in WFInstance.objects.order_by().filter(current_actor=eski_rol, name=wf_name):
                    wfi.current_actor = yeni_rol
                    wfi.blocking_save(query_dict={'current_actor': yeni_rol})
                    instances.append(wfi.key)

                for inv in TaskInvitation.objects.order_by().filter(progress__in=[20, 30],
                                                         role=eski_rol,
                                                         wf_name=wf_name,
                                                         instance_id__in=instances):
                    inv.role_id = yeni_rol.key
                    inv.blocking_save(query_dict={'role_id': yeni_rol.key})

        else:
            silinecek_roller = [rs.role for rs in personel.user.role_set]

        if len(silinecek_roller) > 0:
            for r in silinecek_roller:
                r.blocking_delete()

        personel.arsiv = True
        personel.save()

    def bilgilendirme(self):
        personel = Personel.objects.get(self.current.task_data['personel_id'])
        self.current.output['msgbox'] = {
            "type": "info",
            "title": _(u"Ayrılma İşlemi Başarıyla Gerçekleşti"),
            "msg": _(u"%(ad)s %(soyad)s adlı personel işten ayrıldı.") % {
                'ad': personel.ad,
                'soyad': personel.soyad
            }
        }

    def anasayfa_yonlendirme(self):
        """
            Iptal isleminden sonra ana sayfa ekrani yuklenir.
        """
        self.current.output['cmd'] = 'reload'

    def engelli_personel_kontrol(self, personel):
        engelli_dereceleri = [2, 3, 4]
        engelli_personel_sayisi = personel.objects.filter(
            engel_derecesi__in=engelli_dereceleri).count()
        toplam_personel_sayisi = Personel.objects.count()

        engelli_personel_kontrol = toplam_personel_sayisi * self.engelli_personel_katsayisi

        if engelli_personel_sayisi < engelli_personel_kontrol \
                and personel.engel_derecesi in engelli_dereceleri:
            uyari_mesaji = """
* İlgili personeli silmeniz halinde, engelli personel sayısı yasal

    sınırın altına düşecektir.

    Engelli personel sayısı: %s,

    Toplam personel sayısı: %s.

""" % (engelli_personel_sayisi, toplam_personel_sayisi)
            self.current.task_data['uyari_mesaji'] = uyari_mesaji

    def zorunlu_hizmet_kontrolu(self, ayrilma_tarihi, mecburi_gorev_tarihi):
        if mecburi_gorev_tarihi > ayrilma_tarihi:
            uyari_mesaji = """

* Personele ait zorunlu görev süresi dolmamıştır.

    %s tarihine kadar devam etmektedir!""" % mecburi_gorev_tarihi

            if 'uyari_mesaji' in self.current.task_data:
                self.current.task_data['uyari_mesaji'] += uyari_mesaji
            else:
                self.current.task_data['uyari_mesaji'] = uyari_mesaji
