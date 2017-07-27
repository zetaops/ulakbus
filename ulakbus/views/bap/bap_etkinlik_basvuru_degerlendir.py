# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import Role
from ulakbus.models import User
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __


class EtkinlikBasvuruDegerlendirForm(JsonForm):
    class Meta:
        title = _(u"Etkinlik Başvuru Değerlendir")

    class Butce(ListNode):
        talep_turu = fields.Integer(__(u"Talep Türü"), required=True,
                                    choices='bap_bilimseL_etkinlik_butce_talep_turleri')
        istenen_tutar = fields.Float(__(u"Talep Edilen Tutar"), required=True)

    daha_sonra_degerlendir = fields.Button(_(u"Daha Sonra Değerlendir"),
                                           cmd='daha_sonra_degerlendir')
    reddet = fields.Button(_(u"Reddet"), cmd='reddet')
    onayla = fields.Button(_(u"Onayla"), cmd='onayla')


class BAPEtkinlikBasvuruDegerlendir(CrudView):
    """
    Komisyon üyesi veya hakemin etkinlik başvurusu değerlendirmesi yaptığı iş akışıdır.
    """
    class Meta:
        model = 'BAPEtkinlikProje'

    def __init__(self, current=None):
        super(BAPEtkinlikBasvuruDegerlendir, self).__init__(current)
        # Task invitation oluşturulurken etkinlik id'si task data içine yerleştirilir. Eğer task
        # datada yoksa listeleme iş akışından gelindiği varsayılarak gelen inputtan alınır.
        key = self.current.task_data['etkinlik_basvuru_id'] = self.input.get(
            'object_id', False) or self.current.task_data.get('etkinlik_basvuru_id', False)
        self.object = BAPEtkinlikProje.objects.get(key)

    def basvuru_degerlendir(self):
        """
        Komisyon üyesi veya hakemin etkinlik başvurusunu değerlendirdiği adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        self.show()
        form = EtkinlikBasvuruDegerlendirForm()
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def daha_sonra_degerlendir(self):
        """
        Komisyon üyesi daha sonra değerlendir butonuna tıklayarak etkinlik başvurusunu daha sonra
         değerlendirmeyi seçebilir. Daha sonra etkinlik başvurusuna görev yöneticisinden ulaşabilir.
        """
        self.current.output['cmd'] = 'reload'

    def reddet(self):
        """
        Etkinlik başvurusunun reddedildiği adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        msg = _(u"%s başlıklı bilimsel etkinlik projesi başvurunuz reddedilmiştir." %
                etkinlik.bildiri_basligi)
        self.red_onay(etkinlik, 3, msg)
        self.current.output['cmd'] = 'reload'

    def onayla(self):
        """
        Etkinlik başvurusunun onaylandığı adımdır.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        msg = _(u"%s başlıklı bilimsel etkinlik projesi başvurunuz onaylanmıştır." %
                etkinlik.bildiri_basligi)
        self.red_onay(etkinlik, 2, msg)
        self.current.output['cmd'] = 'reload'

    def red_onay(self, etkinlik, durum, msg):
        etkinlik.durum = durum
        etkinlik.blocking_save()
        role = Role.objects.filter(user=etkinlik.basvuru_yapan.personel.user)[0]
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        role.send_notification(title=_(u"Bilimsel Etkinlik Projesi Başvurusu"),
                               message=msg,
                               typ=1,
                               sender=sistem_user
                               )
