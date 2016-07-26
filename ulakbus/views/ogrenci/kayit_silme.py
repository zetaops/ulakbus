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

ABSTRACT_ROLE_LIST = [
    "Lisans Programı Öğrencisi - Aktif",
    "Lisans Programı Öğrencisi - Kayıt Dondurmuş",

    "Ön Lisans Programı Öğrencisi - Aktif",
    "Ön Lisans Programı Öğrencisi - Kayıt Dondurmuş",

    "Yüksek Lisans Programı Öğrencisi - Aktif",
    "Yüksek Lisans Programı Öğrencisi - Kayıt Dondurmuş",

    "Doktora Programı Öğrencisi - Aktif",
    "Doktora Programı Öğrencisi - Kayıt Dondurmuş",

]

ABSTRACT_ROLE_LIST_SILINMIS = [
    "Lisans Programı Öğrencisi - Kayıt Silinmiş",
    "Ön Lisans Programı Öğrencisi - Kayıt Silinmiş",
    "Yüksek Lisans Programı Öğrencisi - Kayıt Silinmiş",
    "Doktora Programı Öğrencisi - Kayıt Silinmiş",
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
                name = role.abstract_role.name
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
            'type': 'warning', "title": 'Kayıt Silme Başarılı',
            "msg": ' %s adlı öğrencinin kaydı daha önceden silinmiştir.' % ogrenci

        }

    def kayit_silme_islemini_onayla(self):
        """
        Personele kayıt silme işlemine devam etmek isteyip istemediği sorulur.

        """

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        _form = JsonForm(current=self.current,
                         title='Kayıt Silme İşlemini Onaylayınız.')
        _form.help_text = '%s adlı öğrencinin %s rollerini silmek üzerisiniz. Emin misiniz?' % (
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
            'type': 'warning', "title": 'Kayıt Silme İşlemi',
            "msg": 'Kayıt silme işlemi iptal edilmiştir.'

        }

    def fakulte_yonetim_karari(self):
        """
        Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

        """

        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        _form = JsonForm(current=self.current,
                         title='Fakülte Yönetim Kurulunun Karar Numarasını Giriniz.')
        _form.karar = fields.String('Karar No', index=True)
        _form.kaydet = fields.Button('Kaydet')
        self.form_out(_form)

    def ayrilma_nedeni_sec(self):
        """
        Ayrılma nedenlerini form içinde listelenir. Listelenen ayrılma nedenlerinden biri
        kullanıcı tarafından seçilir.

        """

        _form = JsonForm(current=self.current, title='Öğrencinin Ayrılma Nedenini Seçiniz')
        _form.ayrilma_nedeni = fields.Integer(choices=self.object.get_choices_for('ayrilma_nedeni'))
        _form.aciklama = fields.Text("Açıklama Yazınız", required=True)
        _form.sec = fields.Button("Seç")
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

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        programlar = OgrenciProgram.objects.filter(ogrenci_id=self.current.task_data['ogrenci_id'])
        for program in programlar:
            program.ayrilma_nedeni = self.current.input['form']['ayrilma_nedeni']
            # todo: elle vermek yerine daha iyi bir yol dusunelim
            program.ogrencilik_statusu = 21
            program.save()
            roles = Role.objects.filter(user=ogrenci.user, unit=program.program.birim)
            for role in roles:
                if role.abstract_role.name in ABSTRACT_ROLE_LIST:
                    if role.unit.unit_type == 'Program':
                        abstract_role = AbstractRole.objects.get(
                            name=ABSTRACT_ROLE_LIST_SILINMIS[0])
                        role.abstract_role = abstract_role
                        role.save()
                    elif role.unit.unit_type == 'Yüksek Lisans Programı':
                        abstract_role = AbstractRole.objects.get(
                            name=ABSTRACT_ROLE_LIST_SILINMIS[2])
                        role.abstract_role = abstract_role
                        role.save()
                    elif role.unit.unit_type == 'Doktora Programı':
                        abstract_role = AbstractRole.objects.get(
                            name=ABSTRACT_ROLE_LIST_SILINMIS[3])
                        role.abstract_role = abstract_role
                        role.save()
                    else:
                        abstract_role = AbstractRole.objects.get(
                            name=ABSTRACT_ROLE_LIST_SILINMIS[1])
                        role.abstract_role = abstract_role
                        role.save()

        ogrenci_rolleri = Role.objects.filter(user=ogrenci.user)
        for role in ogrenci_rolleri:
            if role.abstract_role.name not in ABSTRACT_ROLE_LIST_SILINMIS:
                title = 'Kayıt Silme'
                msg = """%s adlı öğrencinin kaydı silinmiştir.
                         Öğrenci farklı rollere sahiptir.""" % ogrenci

                # TODO: sistem yoneticisine bilgi ver.
                usr = User.objects.get(username='ulakbus')
                self.notify(usr, msg=msg, title=title)
                break

    def bilgi_ver(self):
        """
        Kayıt silme iş akışı tamamlandıktan sonra danışmana ve öğrenciye bilgi verilir.
        Kayıt silme işleminin tamamlandığına dair ekrana çıktı verir.

        """
        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci=ogrenci)
        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Kayıt Silme',
            "msg": 'Öğrencinin kaydı %s nedeniyle silinmiştir.' % self.current.input['form'][
                'aciklama']
        }
        title = 'Kayıt Silme'
        msg = '%s adlı öğrencinin kaydı %s nedeniyle silinmiştir.' % (
            ogrenci, self.current.input['form']['aciklama'])

        for program in ogrenci_program:
            self.notify(program.danisman.user, title=title, msg=msg)

        self.notify(ogrenci.user, title=title, msg=msg)

    @staticmethod
    def notify(user, msg, title):
        if user:
            user.send_notification(message=msg, title=title)

