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
        pass

    def _diger_hizmet_hesapla(self):
        pass

    def _yurtdisi_2_3_hesapla(self):
        pass

    def _yurtdisi_3_4_hesapla(self):
        pass

    def _yurtdisi_tum_hesapla(self):
        pass

    def _fiili_hizmet_hesapla(self):
        pass

    def _ssk_2_3_hesapla(self):
        pass

    def _ssk_3_4_hesapla(self):
        pass

    def _ssk_kamu_hesapla(self):
        pass

    def _ssk_tum_hesapla(self):
        pass

    def _bagkur_2_3_hesapla(self):
        pass

    def _bagkur_3_4_hesapla(self):
        pass

    def _bagkur_tum_hesapla(self):
        pass

    def _askerlik_hesapla(self):
        pass

    def _fahri_gorev_hesapla(self):
        pass

    def _yurtdisi_egitim_hesapla(self):
        pass

    def _ucretsiz_izin_hesapla(self):
        pass