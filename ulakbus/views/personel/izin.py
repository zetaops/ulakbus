# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView, obj_filter
from pyoko import form

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Personel

class IzinIslemleri(CrudView):

    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Izin'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        # object_actions = [
        #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        # ]

    # class ObjectForm(JsonForm):
    #     class Meta:
    #         # durum alanini formdan cikar. kadrolar sadece sakli olarak kaydedilebilir.
    #         exclude = ['personel', 'vekil', ]
    #
    #     save_edit = form.Button("Kaydet", cmd="save")

    #
    # ObjectForm birden cok view da farklilasiyorsa metod icinde bu sekilde kullanilmali.
    #
    # def kadro_ekle_form(self):
    #     self.object_form.exclude = ['durum',]
    #     self.form()
    #

    # def izin_kaydet(self):
    #     # formdan gelen datayi, instance a gecir.
    #     self.set_form_data_to_object()
    #     print self.object
    #
    #     # Kadroyu kaydet
    #     self.object.save()
    #
    #     # isakisini bastan baslat
    #     self.reset()

    def goster(self):
        self.list()
        personel = Personel.objects.get(self.input['personel_id'])
        izin = self.izin_hesapla(personel)
        self.output['object'] = { "Adı":personel.ad, "Kalan İzin":"30" }

        # Formun üzerinde gösterilen bilgilerin başlığı
        # set edilmezse {add=null} görünüyor
        self.output['forms']['model'] = personel.ad + " izin bilgileri"

    def izin_hesapla(self,personel):
        from datetime import datetime
        self.ge
        for izin in self.output['objects']:
            izin.fields
            print

        pass
