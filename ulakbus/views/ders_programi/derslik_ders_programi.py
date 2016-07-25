# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from collections import OrderedDict

from ulakbus.models import DersEtkinligi, Room
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView


class DerslikSecimFormu(JsonForm):
    """
    Derslik Seç adımında kullanılan formdur.

    """
    ileri = fields.Button("İleri")


class DerslikDersProgrami(CrudView):
    """ Derslik Ders Programı İş Akışı
    Derslik Ders Programi,bir bölümün sahip olduğu dersliklere ait ders programlarını gösterir ve
    kullanıcının ders programlarını yazdırabilmesine olanak sağlar.

    Bu iş akışı 2 adımdan oluşur.

    Derslik Seç:
    Derslikler listelenir.

    Derslik Ders Programını Göster:
    Seçilen dersliğe ait ders programlarını ekrana basar.

    """
    class Meta:
        model = 'DersEtkinligi'

    def derslik_sec(self):
        """
        Derslikler listelenir.

        """
        _form = DerslikSecimFormu(title='Derslik Seçiniz', current=self.current)
        ders_etkinlikleri = DersEtkinligi.objects.filter(solved=True)
        _choices = [(_etkinlik.room.key, _etkinlik.room.__unicode__()) for _etkinlik in ders_etkinlikleri]
        _form.derslik = fields.Integer(choices=_choices)
        self.form_out(_form)

    def derslik_ders_programini_goster(self):
        """
        Seçilen dersliğe ait ders programlarını ekrana basar.
        .. code-block:: python
            # response:
            {
                'derslik_ders_programlari': {
                    'zaman_plani': [{
                        'ders': string,   # ders nesnesinin __unicode__ metotu çağrılır
                        'baslangic_saati': string,  # 10:00,
                        'bitis_saati': string,  # 12:00,
                        'gun': string,     # pazartesi,
                        }]}
            }
        """

        room = Room.objects.get(self.current.input['form']['derslik'])
        derslik_zaman_plani = []
        for d_etkinligi in DersEtkinligi.objects.filter(room=room):
            data_lst = OrderedDict({})
            data_lst['ders'] = d_etkinligi.ders.__unicode__()
            data_lst['gun'] = d_etkinligi.get_gun_display()
            data_lst['baslangic_saati'] = d_etkinligi.baslangic_saat + ':' + d_etkinligi.baslangic_dakika
            data_lst['bitis_saati'] = d_etkinligi.bitis_saat + ':' + d_etkinligi.bitis_dakika
            derslik_zaman_plani.append(data_lst)
        item = {'zaman_plani': derslik_zaman_plani}
        self.output['derslik_ders_programlari'] = item
        _form = JsonForm(title="%s Dersliğine Ait Ders Programları" % room.__unicode__())
        _form.yazdir = fields.Button('Pdf yazdır')
        self.form_out(_form)
