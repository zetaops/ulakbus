# -*-  coding: utf-8 -*-

from datetime import timedelta, date, datetime

from ulakbus.models.hitap.hitap import HizmetKayitlari, HizmetBirlestirme
from ulakbus.models.personel import Personel, Izin


class HizmetSureleri():

    personel = None

    def __init__(self,personel=None,tckn=None):
        if personel:
            self.personel = personel
        elif tckn:
            self.personel = Personel.objects.filter(tckn=tckn)[0]

    def fiili_hizmet_getir(self):
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn,sgk_nevi__in=[3, 7, 4, 1,2, 6 ])

        sure = 0
        for hizmet in hizmetler:
            sure += hizmet.sure
        sure += self._emekli_sandigi_hesapla()

        return sure
        return self._emekli_sandigi_hesapla() + self._bagkur_tum_hesapla() \
                + self._diger_hizmet_hesapla() + self._yurtdisi_tum_hesapla() \
                + self._fiili_hizmet_hesapla() + self._ssk_tum_hesapla() \
                + self._askerlik_hesapla() + self._ucretsiz_izin_hesapla() \
                + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def fiili_hizmet_ayrinti(self):
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "bagkur_tum": self._bagkur_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "fiili_hizmet": self._fiili_hizmet_hesapla(), "ssk_tum": self._ssk_tum_hesapla(),
                "askerlik_hesapla": self._askerlik_hesapla(), "ucretsiz_izin": self._ucretsiz_izin_hesapla(),
                "fahri_gorev": self._fahri_gorev_hesapla(), "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def kidem_hizmet_getir(self):
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
                + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
                + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
                + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def kidem_hizmet_ayrinti(self):
        return { "emekli_sandigi": self._emekli_sandigi_hesapla(), "askerlik_hesapla": self._askerlik_hesapla(),
                 "ssk_2_3" : self._ssk_2_3_hesapla(), "ssk_3_4" : self._ssk_3_4_hesapla(),
                 "ssk_kamu" : self._ssk_kamu_hesapla(), "bagkur_2_3" : self._bagkur_2_3_hesapla(),
                 "bagkur_3_4" : self._bagkur_3_4_hesapla(), "yurtdisi_2_3": self.yurtdisi_2_3_hesapla(),
                "yurtdisi_3_4": self._yurtdisi_3_4_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "fahri_gorev": self._fahri_gorev_hesapla(),
                 "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
            }

    def izin_hizmet_getir(self):
        return self._emekli_sandigi_hesapla() + self._askerlik_hesapla() \
               + self._ssk_tum_hesapla() + self._bagkur_tum_hesapla() \
               + self._yurtdisi_tum_hesapla() + self._diger_hizmet_hesapla() \
               + self._fahri_gorev_hesapla() + self._yurtdisi_egitim_hesapla()

    def izin_hizmet_ayrinti(self):
        return {"emekli_sandigi": self._emekli_sandigi_hesapla(), "askerlik_hesapla": self._askerlik_hesapla(),
                "ssk_2_3": self._ssk_2_3_hesapla(), "ssk_3_4": self._ssk_3_4_hesapla(),
                "ssk_kamu": self._ssk_kamu_hesapla(), "bagkur_2_3": self._bagkur_2_3_hesapla(),
                "bagkur_3_4": self._bagkur_3_4_hesapla(), "yurtdisi_2_3": self.yurtdisi_2_3_hesapla(),
                "yurtdisi_3_4": self._yurtdisi_3_4_hesapla(), "yurtdisi_tum": self._yurtdisi_tum_hesapla(),
                "diger_hizmet": self._diger_hizmet_hesapla(), "fahri_gorev": self._fahri_gorev_hesapla(),
                "yurtdisi_egitim": self._yurtdisi_egitim_hesapla()
                }

    """
    Aşağıdaki fonksiyonlar yanlızca bu class içinde kullanılacaktır. İhtiyaç olan yerlerde
    üstteki fonksiyonlar çağırılacaktır.

    """

    def _emekli_sandigi_hesapla(self):
        hizmetler = HizmetKayitlari.objects.filter(tckn=self.personel.tckn).order_by("order_date")

        baslangic = None
        sure = 0

        for hizmet in hizmetler:
            if hizmet.sebep_kod.nevi == 1:
                baslangic = hizmet.baslama_tarihi
            elif hizmet.sebep_kod.nevi == 2:
                sure += (hizmet.bitis_tarihi - baslangic).days

        if baslangic:
            sure += (date.today() - baslangic).days

        return sure

    def _diger_hizmet_hesapla(self):
        return 0

    def _yurtdisi_2_3_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 1 - 2/3
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4], kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_3_4_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri / kha_durum = 2 - 3/4
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _yurtdisi_tum_hesapla(self):
        # sgk_nevi = 4 / Yurt Dışı Hizmetleri
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[4])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _fiili_hizmet_hesapla(self):
        return 0

    def _ssk_2_3_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_3_4_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_kamu_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _ssk_tum_hesapla(self):
        # sgk_nevi = 1 / SSK Kamu - 2 / SSK Özel - 12 / SSK FHZ (01/10/2008 Sonrası İçin)
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[1, 2, 12])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_2_3_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=1)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_3_4_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3],kha_durum=2)

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _bagkur_tum_hesapla(self):
        # sgk_nevi = 3 / Bağ-Kur
        hizmetler = HizmetBirlestirme.objects.filter(tckn=self.personel.tckn, sgk_nevi__in=[3])

        sure = 0
        for hizmet in hizmetler:
            sure += int(hizmet.sure)

        return sure

    def _askerlik_hesapla(self):
        return 0

    def _fahri_gorev_hesapla(self):
        return 0

    def _yurtdisi_egitim_hesapla(self):
        return 0

    def _ucretsiz_izin_hesapla(self):
        return 0