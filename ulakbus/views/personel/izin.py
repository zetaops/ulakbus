# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView, obj_filter
from pyoko import form

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Personel
from ulakbus.models.hitap import HizmetKayitlari, HizmetBirlestirme
from datetime import timedelta, date


class IzinIslemleri(CrudView):
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'Izin'

        # ozel bir eylem listesi hazirlayacagiz. bu sebeple listeyi bosaltiyoruz.
        # kayit tipine bagli olarak ekleyecegimiz eylemleri .append() ile ekleyecegiz
        # object_actions = [
        #     # {'fields': [0, ], 'cmd': 'show', 'mode': 'normal', 'show_as': 'link'},
        # ]

    def goster(self):
        yil = date.today().year
        self.list()
        personel = Personel.objects.get(self.input['id'])
        izin_gun = self.hizmet_izin_yil_hesapla(personel)
        kalan_izin = self.kalan_izin_hesapla()
        bu_yil_kalan_izin = getattr(kalan_izin['yillik'], str(yil), 0)
        gecen_yil_kalan_izin = getattr(kalan_izin['yillik'], str(yil - 1), 0)
        kalan_mazeret_izin = getattr(kalan_izin['mazeret'], str(yil), 0)

        # Personelin izin gün sayısı 365 günden azsa eklemeyi kaldır.
        # Personel pasifse eklemeyi kaldır.
        yil = date.today().year
        izin_hakki_yok_sartlari = [
            izin_gun < 365,
            self.personel_aktif,
            bu_yil_kalan_izin <= 0 and gecen_yil_kalan_izin <= 0 and kalan_mazeret_izin <= 0
        ]
        if any(izin_hakki_yok_sartlari):
            self.ListForm.add = None

        # TODO: Personel bilgileri tabloda gösterilecek
        self.output['object'] = {
            "type": "table",
            "fields": [
                {
                    "name": personel.ad,
                    "surname": personel.soyad
                },
                {
                    "gun": izin_gun,
                    "durum": "Aktif" if self.personel_aktif else "Pasif"
                }, {
                    "izinler": kalan_izin,
                    "hizmet_sure": izin_gun
                }
            ]
        }

    def emekli_sandigi_hesapla(self, personel):
        personel_hizmetler = HizmetKayitlari.objects.filter(tckn=personel.tckn)

        baslangic_liste = set()
        bitis_liste = set()

        for hizmet in personel_hizmetler:
            baslangic_liste.add(hizmet.baslama_tarihi)
            bitis_liste.add(hizmet.bitis_tarihi)

        # clean sets any of blank dates
        blank_dates = [date(1900, 1, 1), '']
        for d in blank_dates:
            if d in baslangic_liste:
                baslangic_liste.remove(d)
            if d in bitis_liste:
                bitis_liste.remove(d)

        # sort dates
        baslangic_liste = sorted(baslangic_liste)
        bitis_liste = sorted(bitis_liste)

        if len(baslangic_liste) > 0:
            self.ilk_izin_hakedis = baslangic_liste[0] + timedelta(365)
        else:
            self.ilk_izin_hakedis = date.today()

        toplam_sure = timedelta(0)
        son_baslama = None

        for baslangic in baslangic_liste:
            if son_baslama is None:
                son_baslama = baslangic
            elif len(bitis_liste) > 0 and baslangic >= bitis_liste[0]:
                toplam_sure += bitis_liste[0] - son_baslama
                son_baslama = baslangic
                bitis_liste.remove(bitis_liste[0])

        if son_baslama is None:
            personel_aktif = False
        elif len(bitis_liste) > 0:
            personel_aktif = False
            toplam_sure += bitis_liste[0] - son_baslama
        else:
            personel_aktif = True
            toplam_sure += date.today() - son_baslama

        # print str(int(toplam_sure.days / 360)) + " Yıl, " + str(int(toplam_sure.days % 360)) + " Gün"
        return toplam_sure.days, personel_aktif

    @staticmethod
    def sgk_hesapla(personel):
        personel_birlestirmeler = HizmetBirlestirme.objects.filter(tckn=personel.tckn)
        toplam_gun = 0

        for hizmet in personel_birlestirmeler:
            toplam_gun += hizmet.sure

        return toplam_gun

    def hizmet_izin_yil_hesapla(self, personel):
        emekli_sandigi_gun, aktif = self.emekli_sandigi_hesapla(personel)
        sgk_gun = self.sgk_hesapla(personel)
        self.personel_aktif = aktif
        return emekli_sandigi_gun + sgk_gun

    def kalan_izin_hesapla(self):
        query = self._apply_list_queries(self.object.objects.filter())
        yillik_izinler = dict()
        mazeret_izinler = dict()

        for yil in range(self.ilk_izin_hakedis.year, date.today().year + 1):
            yillik_izinler[yil] = 20
            mazeret_izinler[yil] = 10

        for izin in query:
            if izin.tip == 1:
                yil = izin.baslangic.year - 1
                if yil in yillik_izinler.keys() and yillik_izinler[yil] > 0:
                    yillik_izinler[yil] -= (izin.bitis - izin.baslangic).days
                else:
                    yil += 1
                    yillik_izinler[yil] -= (izin.bitis - izin.baslangic).days
            elif izin.tip == 5:
                mazeret_izinler[yil] -= (izin.bitis - izin.baslangic).days

        return {'yillik': yillik_izinler, 'mazeret': mazeret_izinler}
