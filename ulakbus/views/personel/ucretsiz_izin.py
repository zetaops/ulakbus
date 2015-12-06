# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView, obj_filter
from pyoko import form

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Personel,UcretsizIzin
from datetime import timedelta,date

class UcretsizIzinIslemleri(CrudView):

    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'UcretsizIzin'

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

    class ListForm(JsonForm):
        btn = form.Button("Ücretsiz İzine Ayır",cmd="izine_ayir") # default

    class IzinForm(JsonForm):
        class Meta:
            include = ['tip','baslangic','bitis','onay','personel']

        kaydet = form.Button("Kaydet",next="izine_ayir",cmd="save")

    class DonusForm(JsonForm):
        class Meta:
            include = ['donus_tarihi','donus_tip']

        kaydet = form.Button("Kaydet",next="izin_donus",cmd="save")


    def goster(self):
        if 'personel_id' in self.input:
            personel = Personel.objects.get(self.input['personel_id'])

            ucretsiz_izinler = UcretsizIzin.objects.filter(personel=personel)
            ucretsiz_izinde = False

            for izin in ucretsiz_izinler:
                if izin.donus_tarihi == None or izin.donus_tarihi == "":
                    ucretsiz_izinde = True
                    self.current.task_data['object_id'] = izin.key
                    self.object = izin
                    break

            if ucretsiz_izinde:
                self.ListForm.btn = form.Button("Ücretsiz İzin Dönüşü",cmd="izin_donus")
            else:
                self.ListForm.btn = form.Button("Ücretsiz İzine Ayır",cmd="izine_ayir")
        else:
            pass

        self.list()


    def izine_ayir(self):
        self.form_out(self.IzinForm(self.object, current=self.current))


    def izin_donusu(self):
        # personel = Personel.objects.get(self.input['personel_id'])
        # ucretsiz_izinler = UcretsizIzin.objects.filter(personel=personel)
        #
        # for izin in ucretsiz_izinler:
        #     if izin.donus_tarihi == None or izin.donus_tarihi == "":
        #         self.object = izin
        #         break

        self.form_out(self.DonusForm(self.object, current=self.current))