# -*-  coding: utf-8 -*-

from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.lib.hizmet_sureleri import HizmetSureleri

class HizmetSureleriView(CrudView):

    class Meta:
        model = 'Personel'

    def sure_gosterim_duzenle(self, sure):
        """
        parametre olarak girilen gün sayısını yıl ay gün formatına çevirir.
        Örnek:
            2127 integer değeri parametre olarak verilirse, metod
            '5 Yıl 10 Ay 27 Gün' string değerini return eder.
        Args:
            sure: integer

        Returns:

        """
        if sure == 0:
            return 0
        else:
            yildan_kalan = sure % 360
            sure -= yildan_kalan
            yil = sure / 360
            aydan_kalan = yildan_kalan % 30
            yildan_kalan -= aydan_kalan
            ay = yildan_kalan / 30
            return "{yil} Yıl {ay} Ay {gun} Gun".format(
                yil = yil,
                ay = ay,
                gun = aydan_kalan
            )

    def goster(self):
        """
        Hizmet sürelerini bir tablo halinde ekrana basan metoddur.
        Returns:

        """
        p = self.object
        self.output['object_title'] = "Personel: {0} {1} Hizmet Süreleri".format(p.ad, p.soyad)

        hs = HizmetSureleri(personel=p)
        fiili_hizmet = hs.fiili_hizmet_ayrinti()
        kidem_hizmet = hs.kidem_hizmet_ayrinti()
        izin_hizmet = hs.izin_hizmet_ayrinti()

        output = [{0: (u'Fiili Hizmet'),
                   1: (u'Kıdem Hizmeti'),
                   2: (u'İzin Hizmeti')}]

        self.current.output['objects'] = output

        hesaplanan_fiili_hizmet = """
        Emekli Sandığı: {fiili_hizmet_emekli_sandigi}

        Bağkur(Tüm): {fiili_hizmet_bagkur_tum}

        Diğer Hizmetler:  {fiili_hizmet_diger_hizmet}

        Yurtdışı (Tüm): {fiili_hizmet_yurtdisi_tum}

        Fiili İtibar: {fiili_hizmet_fiili_hizmet}

        SSK (Tüm): {fiili_hizmet_ssk_tum}

        Askerlik: {fiili_hizmet_askerlik_hesapla}

        Ücretsiz İzin: {fiili_hizmet_ucretsiz_izin}

        Fahri Görev: {fiili_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {fiili_hizmet_yurtdisi_egitim}
        """.format(
            fiili_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(fiili_hizmet['emekli_sandigi']),
            fiili_hizmet_bagkur_tum=self.sure_gosterim_duzenle(fiili_hizmet['bagkur_tum']),
            fiili_hizmet_diger_hizmet=self.sure_gosterim_duzenle(fiili_hizmet['diger_hizmet']),
            fiili_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(fiili_hizmet['yurtdisi_tum']),
            fiili_hizmet_fiili_hizmet=self.sure_gosterim_duzenle(fiili_hizmet['fiili_hizmet']),
            fiili_hizmet_ssk_tum=self.sure_gosterim_duzenle(fiili_hizmet['ssk_tum']),
            fiili_hizmet_askerlik_hesapla=self.sure_gosterim_duzenle(fiili_hizmet['askerlik_hesapla']),
            fiili_hizmet_ucretsiz_izin=self.sure_gosterim_duzenle(fiili_hizmet['ucretsiz_izin']),
            fiili_hizmet_fahri_gorev=self.sure_gosterim_duzenle(fiili_hizmet['fahri_gorev']),
            fiili_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(fiili_hizmet['yurtdisi_egitim'])
        )

        hesaplanan_kidem_hizmeti = """
        Emekli Sandığı: {kidem_hizmet_emekli_sandigi}

        Bağkur(2/3): {kidem_hizmet_bagkur_2_3}

        Bağkur(3/4): {kidem_hizmet_bagkur_3_4}

        Yurtdışı (2/3): {kidem_hizmet_yurtdisi_2_3}

        Yurtdışı (3/4): {kidem_hizmet_yurtdisi_3_4}

        Yurtdışı (Tüm): {kidem_hizmet_yurtdisi_tum}

        Diğer Hizmetler:  {kidem_hizmet_diger_hizmet}

        SSK (2/3): {kidem_hizmet_ssk_2_3}

        SSK (3/4): {kidem_hizmet_ssk_3_4}

        SSK (Kamu): {kidem_hizmet_ssk_kamu}

        Askerlik: {kidem_hizmet_askerlik_hesapla}

        Fahri Görev: {kidem_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {kidem_hizmet_yurtdisi_egitim}
        """.format(
            kidem_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(kidem_hizmet['emekli_sandigi']),
            kidem_hizmet_bagkur_2_3=self.sure_gosterim_duzenle(kidem_hizmet['bagkur_2_3']),
            kidem_hizmet_bagkur_3_4=self.sure_gosterim_duzenle(kidem_hizmet['bagkur_3_4']),
            kidem_hizmet_yurtdisi_2_3=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_2_3']),
            kidem_hizmet_yurtdisi_3_4=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_3_4']),
            kidem_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_tum']),
            kidem_hizmet_diger_hizmet=self.sure_gosterim_duzenle(kidem_hizmet['diger_hizmet']),
            kidem_hizmet_ssk_2_3=self.sure_gosterim_duzenle(kidem_hizmet['ssk_2_3']),
            kidem_hizmet_ssk_3_4=self.sure_gosterim_duzenle(kidem_hizmet['ssk_3_4']),
            kidem_hizmet_ssk_kamu=self.sure_gosterim_duzenle(kidem_hizmet['ssk_kamu']),
            kidem_hizmet_askerlik_hesapla=self.sure_gosterim_duzenle(kidem_hizmet['askerlik_hesapla']),
            kidem_hizmet_fahri_gorev=self.sure_gosterim_duzenle(kidem_hizmet['fahri_gorev']),
            kidem_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(kidem_hizmet['yurtdisi_egitim'])
        )

        hesaplanan_izin_hizmeti = """
        Emekli Sandığı: {izin_hizmet_emekli_sandigi}

        Bağkur(2/3): {izin_hizmet_bagkur_2_3}

        Bağkur(3/4): {izin_hizmet_bagkur_3_4}

        Yurtdışı (2/3): {izin_hizmet_yurtdisi_2_3}

        Yurtdışı (3/4): {izin_hizmet_yurtdisi_3_4}

        Yurtdışı (Tüm): {izin_hizmet_yurtdisi_tum}

        Diğer Hizmetler:  {izin_hizmet_diger_hizmet}

        SSK (2/3): {izin_hizmet_ssk_2_3}

        SSK (3/4): {izin_hizmet_ssk_3_4}

        SSK (Kamu): {izin_hizmet_ssk_kamu}

        Fahri Görev: {izin_hizmet_fahri_gorev}

        Yurtdışı Eğitim: {izin_hizmet_yurtdisi_egitim}
        """.format(
            izin_hizmet_emekli_sandigi=self.sure_gosterim_duzenle(izin_hizmet['emekli_sandigi']),
            izin_hizmet_bagkur_2_3=self.sure_gosterim_duzenle(izin_hizmet['bagkur_2_3']),
            izin_hizmet_bagkur_3_4=self.sure_gosterim_duzenle(izin_hizmet['bagkur_3_4']),
            izin_hizmet_yurtdisi_2_3=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_2_3']),
            izin_hizmet_yurtdisi_3_4=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_3_4']),
            izin_hizmet_yurtdisi_tum=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_tum']),
            izin_hizmet_diger_hizmet=self.sure_gosterim_duzenle(izin_hizmet['diger_hizmet']),
            izin_hizmet_ssk_2_3=self.sure_gosterim_duzenle(izin_hizmet['ssk_2_3']),
            izin_hizmet_ssk_3_4=self.sure_gosterim_duzenle(izin_hizmet['ssk_3_4']),
            izin_hizmet_ssk_kamu=self.sure_gosterim_duzenle(izin_hizmet['ssk_kamu']),
            izin_hizmet_fahri_gorev=self.sure_gosterim_duzenle(izin_hizmet['fahri_gorev']),
            izin_hizmet_yurtdisi_egitim=self.sure_gosterim_duzenle(izin_hizmet['yurtdisi_egitim'])
        )
        bilgiler = OrderedDict([(0, hesaplanan_fiili_hizmet), (1, hesaplanan_kidem_hizmeti),
                                (2, hesaplanan_izin_hizmeti)])
        item = {
            "type": "table-multiRow",
            "fields": bilgiler,
            "actions": False
        }

        self.current.output['objects'].append(item)