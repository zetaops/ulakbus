# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.forms import JsonForm

from ulakbus.models import OgrenciProgram, Ogrenci, Role, User, AbstractRole
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from ulakbus.lib.role import AbsRole
from ulakbus.lib.ogrenci import kaydi_silinmis_abs_role

ABSTRACT_ROLE_LIST = [
    AbsRole.LISANS_OGRENCISI_AKTIF.name,
    AbsRole.LISANS_OGRENCISI_KAYIT_DONDURMUS.name,

    AbsRole.ON_LISANS_OGRENCISI_AKTIF.name,
    AbsRole.ON_LISANS_OGRENCISI_KAYIT_DONDURMUS.name,

    AbsRole.YUKSEK_LISANS_OGRENCISI_AKTIF.name,
    AbsRole.YUKSEK_LISANS_OGRENCISI_KAYIT_DONDURMUS.name,

    AbsRole.DOKTORA_OGRENCISI_AKTIF.name,
    AbsRole.DOKTORA_OGRENCISI_KAYIT_DONDURMUS.name
]

ABSTRACT_ROLE_LIST_SILINMIS = [
    AbsRole.LISANS_OGRENCISI_KAYIT_SILINMIS.name,
    AbsRole.ON_LISANS_OGRENCISI_KAYIT_SILINMIS.name,
    AbsRole.YUKSEK_LISANS_OGRENCISI_KAYIT_SILINMIS.name,
    AbsRole.DOKTORA_OGRENCISI_KAYIT_SILINMIS.name
]


class KayitSil(CrudView):
    """ Kayıt Silme İş Akışı

    Kayıt silme iş akışı 8 adımdan oluşmaktadır.
    * Kaydı Kontrol Et
    * Kaydı Silinen Öğrenci
    * Kayıt Silme İşlemini Onayla
    * Kayıt Silme İşleminden Vazgeç
    * Fakülte Karar No
    * Ayrılma nedenini seç
    * Öğrenci programı seç
    * Bilgi ver

    Kayıt silme iş akışında öğrencinin kayıtlı olduğu öğrenci programları silinmez,
    öğrencinin kayıtlı olduğu öğrenci programlarının ayrılma nedeni ve öğrencilik
    statüsü field'larına değerler atanır.

    Bu iş akışında kullanılan metotlar şu şekildedir.

    Kaydı Kontrol Et:
    Öğrencinin kaydının silinip silinmediğini kontrol eder.

    Kaydı Silinen Öğrenci:
    Öğrencinin kaydı silinmişse kaydın silindiğine dair bilgi mesajı ekrana basılır.

    Kayıt Silme İşlemini Onayla:
    Personel kayıt silme işlemine devam etmek isteyip istemediği sorulur.

    Kayıt Silme İşleminden Vazgeç:
    Personelin kayıt silme işleminden vazgeçmesi durumunda ekrana silme
    işlemin iptal edildiğine dair bilgi mesajı basılır.

    Fakülte Karar No:
    Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

    Ayrılma nedeni seç:
    Öğrencinin ayrılma nedeni seçilir.

    Öğrenci programı seç:
    Öğrencinin kayıtlı olduğu öğrenci programlarının ayrılık nedeni ve öğrencilik statüsü
    field'larına değerler atanır.

    Bilgi ver:
    Danışmana ve öğrenciye kayıt silme işlemi ile ilgili bilgi verilir.
    Kayıt silme iş akışının son adımıdır. Bu adımdan sonra iş akışı sona erer.

    Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model ``OgrenciProgram``
    modelidir. Meta.model bu amaçla kullanılmıştır.

    Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = 'OgrenciProgram'

    def kontrol(self):
        """
        Öğrencinin kaydının silinip silinmediğini kontrol eder.

        """

        self.current.task_data['command'] = 'kaydi_silinen_ogrenci'
        self.current.task_data['ogrenci_id'] = self.current.input['id']
        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        programlar = OgrenciProgram.objects.filter(ogrenci=ogrenci)
        self.current.task_data['roles'] = []
        for program in programlar:
            roles = Role.objects.filter(user=ogrenci.user, unit=program.program.birim)
            for role in roles:
                self.current.task_data['roles'].append(role.abstract_role.name)
                name = role.abstract_role.key
                if name not in ABSTRACT_ROLE_LIST_SILINMIS and name in ABSTRACT_ROLE_LIST:
                    self.current.task_data['command'] = 'kayit_silme_islemini_onayla'
                    break

    def kaydi_silinen_ogrenci(self):
        """
        Öğrencinin kaydı silinmiş ise öğrenci kaydının silindiğine dair bilgi
        mesajı ekrana basılır.

        """

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Kayıt Silme Başarılı'),
            "msg": _(u' %s adlı öğrencinin kaydı daha önceden silinmiştir.') % ogrenci

        }

    def kayit_silme_islemini_onayla(self):
        """
        Personele kayıt silme işlemine devam etmek isteyip istemediği sorulur.

        """

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        _form = JsonForm(current=self.current,
                         title=_(u'Kayıt Silme İşlemini Onaylayınız.'))
        _form.help_text = _(u'%s adlı öğrencinin %s rollerini silmek üzerisiniz. Emin misiniz?') % (
            ogrenci, '-'.join(
                name for name in self.current.task_data['roles']))
        _form.kaydet = fields.Button('Onayla', flow='fakulte_yonetim_karari')
        _form.vazgecme = fields.Button('Vazgeç', flow='kayit_silme_isleminden_vazgec')
        self.form_out(_form)

    def kayit_silme_isleminden_vazgec(self):
        """
        Personelin kayıt silme işleminden vazgeçmesi durumunda ekrana silme işleminin
        iptal edildiğine dair bilgi mesajı basılır.

        """

        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Kayıt Silme İşlemi'),
            "msg": _(u'Kayıt silme işlemi iptal edilmiştir.')

        }

    def fakulte_yonetim_karari(self):
        """
        Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

        """

        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        _form = JsonForm(current=self.current,
                         title=_(u'Fakülte Yönetim Kurulunun Karar Numarasını Giriniz.'))
        _form.karar = fields.String(_(u'Karar No'), index=True)
        _form.kaydet = fields.Button(_(u'Kaydet'))
        self.form_out(_form)

    def ayrilma_nedeni_sec(self):
        """
        Ayrılma nedenlerini form içinde listelenir. Listelenen ayrılma nedenlerinden biri
        kullanıcı tarafından seçilir.

        """
        self.current.task_data['karar_no'] = self.input['form']['karar']
        _form = JsonForm(current=self.current, title=_(u'Öğrencinin Ayrılma Nedenini Seçiniz'))
        _form.ayrilma_nedeni = fields.Integer(choices=self.object.get_choices_for('ayrilma_nedeni'))
        _form.aciklama = fields.Text(_(u"Açıklama Yazınız"), required=True)
        _form.sec = fields.Button(_(u"Seç"))
        self.form_out(_form)

    def ogrenci_program_sec(self):
        """
        Öğrencinin kayıtlı olduğu öğrenci programların ayrılma nedeni field'larına, ayrılma
        nedeni seç adımındaki ayrılma nedeni atanır.

        Öğrencinin kayıtlı olduğu öğrenci programların öğrencilik statüsüne, ``Kaydı silinmiştir``
        statüsü eklenmiştir.

        Öğrencinin rolü kayıtlı olduğu birimin tipine (program, lisans programı, doktora programı )
        göre değiştirilir.

        Eğer öğrencinin okulda başka bir rolü (kütüphane çalışanı,spor salonu çalışanı) var ise
        admine bilgi mesajı yollanır.

        """
        meta = {'user': self.current.user_id,
                'role': self.current.role_id,
                'wf_name': self.current.workflow_name,
                'task_name': self.current.task_name,
                'reason': 'FAKÜLTE_KARAR_NO_%s' % self.current.task_data['karar_no']}

        index_fields = [('user', 'bin'), ('role', 'bin'), ('wf_name', 'bin'), ('reason', 'bin')]

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        programlar = OgrenciProgram.objects.filter(ogrenci_id=self.current.task_data['ogrenci_id'])
        for program in programlar:
            program.ayrilma_nedeni = self.current.input['form']['ayrilma_nedeni']
            # todo: elle vermek yerine daha iyi bir yol dusunelim
            program.ogrencilik_statusu = 21
            program.save(meta=meta, index_fields=index_fields)
            roles = Role.objects.filter(user=ogrenci.user, unit=program.program.birim)
            for role in roles:
                if role.abstract_role.key in ABSTRACT_ROLE_LIST:
                    abstract_role = kaydi_silinmis_abs_role(role)
                    role.abstract_role = abstract_role
                    role.save(meta=meta, index_fields=index_fields)

        ogrenci_rolleri = Role.objects.filter(user=ogrenci.user)
        for role in ogrenci_rolleri:
            if role.abstract_role.key not in ABSTRACT_ROLE_LIST_SILINMIS:
                title = _(u'Kayıt Silme')
                msg = _(u"""%s adlı öğrencinin kaydı silinmiştir.
                            Öğrenci farklı rollere sahiptir.""") % ogrenci

                # TODO: sistem yoneticisine bilgi ver.
                abstract_role = AbstractRole.objects.get("BASEABSROLE")
                role = Role.objects.get(abstract_role=abstract_role)
                role.send_notification(message=msg, title=title, sender=self.current.user)

    def bilgi_ver(self):
        """
        Kayıt silme iş akışı tamamlandıktan sonra danışmana ve öğrenciye bilgi verilir.
        Kayıt silme işleminin tamamlandığına dair ekrana çıktı verir.

        """
        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci=ogrenci)
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Kayıt Silme'),
            "msg": _(u'Öğrencinin kaydı %s nedeniyle silinmiştir.') % self.current.input['form'][
                'aciklama']
        }
        title = _(u'Kayıt Silme')
        msg = _(u'%s adlı öğrencinin kaydı %s nedeniyle silinmiştir.') % (
            ogrenci, self.current.input['form']['aciklama'])

        for program in ogrenci_program:
            abstract_role = AbstractRole.objects.get("DANISMAN")
            for role in program.danisman.user.role_set:
                if role.role.abstract_role == abstract_role:
                    role.role.send_notification(title=title, message=msg, sender=self.current.user)

        for role in ogrenci.user.role_set:
            abstract_role = kaydi_silinmis_abs_role(role.role)
            if abstract_role.key in ABSTRACT_ROLE_LIST_SILINMIS:
                role.role.send_notification(title=title, message=msg, sender=self.current.user)
