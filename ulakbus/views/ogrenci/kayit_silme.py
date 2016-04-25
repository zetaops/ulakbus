# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.lib.forms import JsonForm

from ulakbus.models import OgrenciProgram, Ogrenci, Role, AbstractRole
from zengine.forms import fields
from zengine.notifications import Notify
from zengine.views.crud import CrudView


class KayitSil(CrudView):
    """ Kayıt Silme İş Akışı

    Kayıt silme iş akışı 4 adımdan oluşmaktadır.
    * Fakülte Karar No
    * Ayrılma nedenini seç
    * Öğrenci programı seç
    * Bilgi ver

    Kayıt silme iş akışında öğrencinin kayıtlı olduğu öğrenci programları silinmez,
    öğrencinin kayıtlı olduğu öğrenci programlarının ayrılma nedeni ve öğrencilik
    statüsü field'larına değerler atanır.

    Bu iş akışında kullanılan metotlar şu şekildedir.

    Fakülte Karar No
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

    def fakulte_yonetim_karari(self):
        """
        Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

        """

        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        self.current.task_data['ogrenci_id'] = self.current.input['id']
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

        """

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        programlar = OgrenciProgram.objects.filter(ogrenci=ogrenci)
        for program in programlar:
            program.ayrilma_nedeni = self.current.input['form']['ayrilma_nedeni']
            # todo: elle vermek yerine daha iyi bir yol dusunelim
            program.ogrencilik_statusu = 21
            program.save()
        abstract_role = AbstractRole.objects.get(name='Silinmiş Öğrenci')
        role = Role.objects.get(user=ogrenci.user)
        role.abstract_role = abstract_role
        role.save()

    def bilgi_ver(self):
        """
        Kayıt silme iş akışı tamamlandıktan sonra danışmana ve öğrenciye bilgi verilir.
        Kayıt silme işleminin tamamlandığına dair ekrana çıktı verir.

        """

        ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_id'])
        ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)
        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Kayıt Silme',
            "msg": 'Öğrencinin kaydı %s nedeniyle silinmiştir.' % self.current.input['form']['aciklama']
        }
        title = 'Kayıt Silme'
        msg = '%s adlı öğrencinin kaydı %s nedeniyle silinmiştir.' % (ogrenci, self.current.input['form']['aciklama'])

        def notify(person):
            Notify(person.user.key).set_message(msg=msg, title=title, typ=Notify.TaskInfo)

        notify(ogrenci_program.danisman)
        notify(ogrenci)