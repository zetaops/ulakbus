# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import BAPEtkinlikProje
from ulakbus.models import BAPGundem
from ulakbus.models import Role
from ulakbus.models import User
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime


class EtkinlikBasvuruGoruntuleForm(JsonForm):
    class Meta:
        title = _(u"Etkinlik Başvuru Görüntüle")

    class Butce(ListNode):
        talep_turu = fields.Integer(__(u"Talep Türü"), required=True,
                                    choices='bap_bilimsel_etkinlik_butce_talep_turleri')
        istenen_tutar = fields.Float(__(u"Talep Edilen Tutar"), required=True)

    daha_sonra_degerlendir = fields.Button(_(u"Daha Sonra Değerlendir"),
                                           cmd='daha_sonra_degerlendir', form_validation=False)

    degerlendirme_kaydet = fields.Button(_(u"Değerlendir"), cmd='degerlendir')


class EtkinlikBasvuruDegerlendirForm(JsonForm):
    class Meta:
        title = _(u"Etkinlik Başvuru Değerlendir")

    aciklama = fields.Text(_(u"Açıklama"), required=False)
    sonuc = fields.Integer(_(u"Değerlendirme Sonucu"), choices='bap_proje_degerlendirme_sonuc')

    degerlendir = fields.Button(_(u"Değerlendirme Kaydet"), cmd='degerlendir')
    daha_sonra_degerlendir = fields.Button(_(u"Daha Sonra Değerlendir"),
                                           cmd='daha_sonra_degerlendir', form_validation=False)

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

    def kontrol(self):
        if self.current.task_data.pop('hakem', False) or self.input.pop('hakem', False):
            self.current.task_data['cmd'] = 'hakem'
        else:
            self.current.task_data['cmd'] = 'komisyon'

    def goruntule(self):
        key = self.current.task_data['etkinlik_basvuru_id']
        self.show()
        form = EtkinlikBasvuruGoruntuleForm()
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def basvuru_degerlendir(self):
        """
        Komisyon üyesi veya hakemin etkinlik başvurusunu değerlendirdiği adımdır.
        """
        form = EtkinlikBasvuruDegerlendirForm()
        self.form_out(form)

    def daha_sonra_degerlendir(self):
        """
        Komisyon üyesi daha sonra değerlendir butonuna tıklayarak etkinlik başvurusunu daha sonra
         değerlendirmeyi seçebilir. Daha sonra etkinlik başvurusuna görev yöneticisinden ulaşabilir.
        """
        self.current.output['cmd'] = 'reload'

    def degerlendirme_kaydet(self):
        """
        Hakem ya da komisyon üyesinin değerlendirmesi kaydedilir ve değerlendirme sonrasında
        otomatik olarak bir gündem nesnesi oluşturulur.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        aciklama = self.input['form']['aciklama']
        sonuc = self.input['form']['sonuc']
        etkinlik.Degerlendirmeler(aciklama=aciklama, degerlendirme_sonuc=sonuc)
        etkinlik.durum = 7
        etkinlik.blocking_save()
        BAPGundem(
            etkinlik=etkinlik,
            gundem_tipi=9
        ).blocking_save()
        role = Role.objects.filter(user=etkinlik.basvuru_yapan.personel.user)[0]
        sistem_user = User.objects.get(username='sistem_bilgilendirme')
        role.send_notification(title=_(u"Bilimsel Etkinlik Projesi Başvurusu"),
                               message=_(u"Etkinlik Başvurunuz Değerlendirilip Gündeme Alınmıştır."),
                               typ=1,
                               sender=sistem_user
                               )

    def basari_mesaji_goster(self):
        """
        Değerlendirmenin başarılı olduğuna dair bir mesaj gösterilir.
        """
        key = self.current.task_data['etkinlik_basvuru_id']
        etkinlik = BAPEtkinlikProje.objects.get(key)
        form = JsonForm(title=_(u"Değerlendirme Başarılı"))
        form.help_text = _(
            u"%s Etkinlik Başvurusunu Başarıyla Değerlendirdiniz" % etkinlik.bildiri_basligi)
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)
