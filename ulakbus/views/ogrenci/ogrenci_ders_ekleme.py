# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Ogrenci, OgrenciDersi, Program, OgrenciProgram, Ders, Donem, Sube, SecmeliDersGruplari, \
    OgretimYili
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView


def sube_arama(current):
    q = current.input.get('query')
    r = []
    subeler = Sube.objects.search_on(*['ders_adi'], contains=q)
    sube_lst = subeler.filter(donem=Donem.guncel_donem())
    for o in sube_lst:
        r.append((o.key, o.__unicode__()))

    current.output['objects'] = r


class DersSecimForm(JsonForm):
    class Meta:
        inline_edit = ['secim']

    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')
        ders_saati = fields.Integer('Ders Saati')
        ders_gunu = fields.String('Ders Günü')
        ders_tipi = fields.String('Ders Tipi')
        secim = fields.Boolean('Seçim', type="checkbox")

    onayla = fields.Button("Onayla")


# class DersOnayForm(JsonForm):
#     class Dersler(ListNode):
#         key = fields.String(hidden=True)
#         ders_adi = fields.String('Ders')
#         ders_saati = fields.Integer('Ders Saati')
#         ders_gunu = fields.String('Ders Günü')
#         ders_tipi = fields.String('Ders Tipi')
#
#     onayla = fields.Button("Onayla")


class OgrenciDersEkleme(CrudView):
    class Meta:
        model = 'Ders'

    @staticmethod
    def basarili_ogrenci_dersleri_bul(eski_donem_ders_kodlari, ogrenci):
        basarili_ders_kodlari = []
        for ders_kodu in eski_donem_ders_kodlari:
            dersler = Ders.objects.filter(kod=ders_kodu)
            for ders in dersler:
                for _sube in ders.sube_set:
                    try:
                        ogrenci_dersi = OgrenciDersi.objects.get(ogrenci=ogrenci, sube=_sube.sube)
                        if ogrenci_dersi.harflendirilmis_not in ['DC', 'CC', 'CB', 'BB', 'BA', 'AA']:
                            ogrenci_dersi_kod = ogrenci_dersi.sube.ders.kod
                            basarili_ders_kodlari.append(ogrenci_dersi_kod)
                    except ObjectDoesNotExist:
                        pass
        return basarili_ders_kodlari

    @staticmethod
    def basarisiz_ogrenci_dersleri_bul(ogrenci):
        eski_donem_ogrenci_dersleri = []
        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], contains='F').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)

        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], startswith='DD').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)
        eski_donem_ders_kodlari = [ogrenci_dersi.sube.ders.kod for ogrenci_dersi in eski_donem_ogrenci_dersleri]
        return eski_donem_ders_kodlari

    @staticmethod
    def yeni_donem_acilan_basarisiz_dersleri_bul(ogrenci_program):
        yeni_donem_basarisiz_dersler = []
        eski_donem_ders_kodlari = OgrenciDersEkleme.basarisiz_ogrenci_dersleri_bul(
            ogrenci_program.ogrenci)
        basarili_ders_kodlari = OgrenciDersEkleme.basarili_ogrenci_dersleri_bul(eski_donem_ders_kodlari,
                                                                                ogrenci_program.ogrenci)
        for ders_kodu in basarili_ders_kodlari:
            if ders_kodu in eski_donem_ders_kodlari:
                eski_donem_ders_kodlari.remove(ders_kodu)
        for ders_kodu in eski_donem_ders_kodlari:
            try:
                ders = Ders.objects.get(kod=ders_kodu, donem=Donem.guncel_donem(), program=ogrenci_program.program)
                yeni_donem_basarisiz_dersler.append(ders)
            except ObjectDoesNotExist:
                dersler = Ders.objects.filter(kod=ders_kodu)
                for ders in dersler:
                    if not ders.donem.guncel:
                        yerine_ders = Ders.objects.get(yerine_ders=ders, donem=Donem.guncel_donem(),
                                                       program=ogrenci_program.program)
                        yeni_donem_basarisiz_dersler.append(yerine_ders)

        return yeni_donem_basarisiz_dersler, basarili_ders_kodlari

    @staticmethod
    def yeni_donem_zorunlu_dersleri_bul(ogrenci_program, yeni_donem_basarisiz_dersler, basarili_ders_kodlari):
        programa_kayitli_zorunlu_dersler = Ders.objects.filter(program=ogrenci_program.program,
                                                               donem=Donem.guncel_donem(),
                                                               zorunlu=True)
        yeni_donem_basarisiz_ders_kodlari = [ders.kod for ders in yeni_donem_basarisiz_dersler]
        zorunlu_dersler = []
        for zorunlu_ders in programa_kayitli_zorunlu_dersler:
            if zorunlu_ders.kod not in yeni_donem_basarisiz_ders_kodlari and zorunlu_ders.kod not in basarili_ders_kodlari:
                zorunlu_dersler.append(zorunlu_ders)
        return zorunlu_dersler

    @staticmethod
    def ders_zamani_kredisi_keyleri_bul(subeler):
        derslerin_keyleri = []
        derslerin_kredileri = []
        derslerin_zamanlari = []
        for item in subeler:
            if item['secim']:
                sube = Sube.objects.get(item['key'])
                derslerin_keyleri.append(sube.ders.key)
                derslerin_kredileri.append(sube.ders.yerel_kredisi)
                # listten kurtar gereksiz
                derslerin_zamanlari.append((item['ders_saati'], item['ders_gunu']))
        return derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari

    @staticmethod
    def ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri):
        d_key = {}
        for ders_key in derslerin_keyleri:
            if ders_key in d_key:
                d_key[ders_key] += 1
            else:
                d_key[ders_key] = 1
        return d_key

    def alttan_kalan_ders_sec(self):
        """
        Subeye saat ve gün fieldları ekelnecek, seçmeli derslerden zorunlu olanlarda eklencek.
        Yeni dönem ait program dersleri listeleneck şubleriyle beraber.

        :return:
        """
        p = Program.objects.get(birim=self.current.role.unit)
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.current.task_data['ogrenci_key'] = ogrenci.key
        ogrenci_program = OgrenciProgram.objects.get(program=p, ogrenci=ogrenci)
        self.current.task_data['danisman_key'] = ogrenci_program.danisman.key
        self.current.task_data['ogrenci_program_key'] = ogrenci_program.key
        kredi = []
        _form = DersSecimForm(title='Alttan Kalan Zorunlu Dersler', current=self.current)
        yeni_donem_basarisiz_dersler, basarili_ders_kodlari = OgrenciDersEkleme.yeni_donem_acilan_basarisiz_dersleri_bul(
            ogrenci_program)
        # self.current.task_data['yeni_donem_basarisiz_dersler'] = [ders.key for ders in yeni_donem_basarisiz_dersler]
        for ders in yeni_donem_basarisiz_dersler:
            if ders.zorunlu:
                for sube in ders.sube_set:
                    for ders_programi in sube.sube.ders_programi_set:
                        _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                      ders_saati=ders_programi.ders_programi.saat,
                                      ders_gunu=ders_programi.ders_programi.gun, ders_tipi='Zorunlu')
                kredi.append(ders.yerel_kredisi)
            else:
                for secmeli_ders in ders.secmeli_ders_gruplari_set:
                    ders_list = [_ders.ders for _ders in secmeli_ders.secmeli_ders_gruplari.Dersler if
                                 _ders.zorunlu_secmeli]
                    self.current.task_data['basarisiz_secmeli_dersler'] = [ders.kod for ders in ders_list]
                    kredi.extend([_ders.yerel_kredisi for _ders in ders_list])
                    sube_list = [_ders.sube_set for _ders in ders_list]
                    for sube in sube_list[0]:
                        for ders_programi in sube.sube.ders_programi_set:
                            _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                          ders_saati=ders_programi.ders_programi.saat,
                                          ders_gunu=ders_programi.ders_programi.gun,
                                          ders_tipi="Seçmeli")
        _form.help_text = "Mininum Krediniz 30, Maximum Krediniz 45dir."
        self.form_out(_form)
        # self.sube_secim_form_inline_edit()
        self.current.output["meta"]["allow_actions"] = False

    def alttan_ders_secimlerini_kontrol_et(self):
        # Kredi kontrolünü yapacaksın
        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['alttan_kalan_ders_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari = \
            OgrenciDersEkleme.ders_zamani_kredisi_keyleri_bul(self.current.task_data['alttan_kalan_ders_subeleri'])
        self.current.task_data['alttan_kalan_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1 or self.current.task_data['alttan_kalan_derslerin_kredileri'] > 45:
                self.current.task_data['alttan_ders_cmd'] = 'alttan_kalan_ders_sec'
                break
            else:
                self.current.task_data['alttan_ders_cmd'] = "guncel_donemden_zorunlu_ders_sec"

    def guncel_donemden_zorunlu_ders_sec(self):
        _form = DersSecimForm(title='Mevcut Dönemin Zorunlu Dersleri', current=self.current)
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        yeni_donem_basarisiz_dersler, basarili_ders_kodlari = OgrenciDersEkleme.yeni_donem_acilan_basarisiz_dersleri_bul(
            ogrenci_program)
        zorunlu_dersler = OgrenciDersEkleme.yeni_donem_zorunlu_dersleri_bul(ogrenci_program,
                                                                            yeni_donem_basarisiz_dersler,
                                                                            basarili_ders_kodlari)
        for ders in zorunlu_dersler:
            for sube in ders.sube_set:
                for ders_programi in sube.sube.ders_programi_set:
                    _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                  ders_saati=ders_programi.ders_programi.saat,
                                  ders_gunu=ders_programi.ders_programi.gun, ders_tipi='Zorunlu')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def guncel_donemden_zorunlu_ders_secimlerini_kontrol_et(self):
        # Kredi kontrolünü yapacaksın
        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['guncel_donemin_zorunlu_derslerin_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari = \
            OgrenciDersEkleme.ders_zamani_kredisi_keyleri_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gd_zorunlu_derslerinin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1:
                self.current.task_data["zorunlu_ders_cmd"] = "guncel_donemden_zorunlu_ders_sec"
                break
            else:
                self.current.task_data["zorunlu_ders_cmd"] = "guncel_donemin_zorunlu_secmeli_derslerini_sec"

    def guncel_donemin_zorunlu_secmeli_derslerini_sec(self):
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        guncel_donem = Donem.guncel_donem()
        if guncel_donem.ad == 'Güz Dönemi':
            yil = guncel_donem.baslangic_tarihi.year
        else:
            yil = guncel_donem.baslangic_tarihi.year - 1
        ogretim_yili = OgretimYili.objects.get(yil=yil)
        # Bir yılın, bir programın ve bir donemin  bir tane seçmeli ders grubu olur
        secmeli_ders = SecmeliDersGruplari.objects.get(program=ogrenci_program.program, ogretim_yili=ogretim_yili,
                                                       donem=ogrenci_program.aktif_donem)
        self.current.task_data['secmeli_ders_key'] = secmeli_ders.key
        _form = DersSecimForm(title='Mevcut Dönemin Zorunlu Seçmeli Dersleri ', current=self.current)
        _form.help_text = 'Minumum seçmeniz gereken seçmeli sayısı %s, Maximum seçmeniz gereken seçmeli sayısı %s' % (
            secmeli_ders.min_sayi, secmeli_ders.max_sayi)
        for ders in secmeli_ders.Dersler:
            if ders.ders.kod not in self.current.task_data['basarisiz_secmeli_dersler']:
                for sube in ders.ders.sube_set:
                    for ders_programi in sube.sube.ders_programi_set:
                        _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                      ders_saati=ders_programi.ders_programi.saat,
                                      ders_gunu=ders_programi.ders_programi.gun, ders_tipi='Seçmeli')

        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def guncel_donemin_zorunlu_secmelilerini_kontrol_et(self):
        # teknik ismi fonksiyonda olmayacak
        # Kredi kontrolünü yapacaksın
        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['guncel_donemin_zorunlu_secmeli_derslerinin_subeleri'] = subeler
        secmeli_ders = SecmeliDersGruplari.objects.get(self.current.task_data["secmeli_ders_key"])
        count = 0
        for ders in self.current.input['form']['Dersler']:
            if ders['secim']:
                count += 1
        derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari = \
            OgrenciDersEkleme.ders_zamani_kredisi_keyleri_bul(self.current.input['form']['Dersler'])
        self.current.task_data['gd_zorunlu_secmelilerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1 or secmeli_ders.max_sayi < count or secmeli_ders.min_sayi > count:
                self.current.task_data["zorunlu_secmeli_cmd"] = "guncel_donemin_secmeli_derslerini_sec"
                break
            else:
                self.current.task_data["zorunlu_secmeli_cmd"] = "ustten_ders_secimini_onayla"

    def ustten_ders_secimini_onayla(self):
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        if ogrenci_program.genel_ortalama >= 3.00:
            _form = JsonForm(title='Üstten Ders Seçimi Onay')
            _form.help_text = "Üstten Ders Seçmek İstiyor musunuz?"
            _form.evet = fields.Button("Evet", flow="ustten_ders_sec")
            _form.hayir = fields.Button("Hayır", flow="farkli_bolumlerden_ders_sec")
            self.form_out(_form)
        else:
            self.current.task_data['flow'] = "farkli_bolumlerden_ders_sec"

    def ustten_ders_sec(self):
        ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
        aktif_donem = ogrenci_program.aktif_donem
        dersler = Ders.objects.filter(program_donemi=aktif_donem + 2, donem=Donem.guncel_donem())
        _form = DersSecimForm(title='Üstten Seçilebilecek Dersler', current=self.current)
        for ders in dersler:
            for sube in ders.sube_set:
                for ders_programi in sube.sube.ders_programi_set:
                    _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                  ders_saati=ders_programi.ders_programi.saat,
                                  ders_gunu=ders_programi.ders_programi.gun, ders_tipi='Üstten')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def ustten_alinan_dersleri_kontrol_et(self):
        subeler = [sube for sube in self.current.input['form']['Dersler'] if sube['secim']]
        self.current.task_data['ustten_alinan_derslerin_subeleri'] = subeler
        derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari = \
            OgrenciDersEkleme.ders_zamani_kredisi_keyleri_bul(self.current.input['form']['Dersler'])
        self.current.task_data['ustten_alinan_derslerin_kredileri'] = sum(derslerin_kredileri)
        d_key = OgrenciDersEkleme.ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1:
                self.current.task_data['secim_command'] = "ustten_ders_sec"
                break
            else:
                self.current.task_data['secim_command'] = "farkli_bolumlerden_ders_sec"

    def farkli_bolumlerden_ders_sec(self):
        butun_derslerin_subeleri = self.current.task_data['ustten_alinan_derslerin_subeleri'] + \
                                   self.current.task_data['guncel_donemin_zorunlu_secmeli_derslerinin_subeleri']+\
                                   self.current.task_data['guncel_donemin_zorunlu_derslerin_subeleri'] +\
                                   self.current.task_data['alttan_kalan_ders_subeleri']
        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        for item in butun_derslerin_subeleri:
            sube = Sube.objects.get(item['key'])
            for ders_programi in sube.ders_programi_set:
                    _form.Dersler(key=sube.key, ders_adi=sube.ders_adi,
                                  ders_saati=ders_programi.ders_programi.saat,
                                  ders_gunu=ders_programi.ders_programi.gun, ders_tipi=item['ders_tipi'])
        self.form_out(_form)
        self.sube_secim_form_inline_edit()

    def butun_dersleri_kontrol_et(self):
        pass

        # @staticmethod
        # def cakisan_dersleri_bul(derslerin_zamanlari):
        #     _dersler = []
        #     _count = 0
        #     for zaman in set(derslerin_zamanlari):
        #         if derslerin_zamanlari.count(zaman) > 1:
        #             _count = derslerin_zamanlari.count(zaman)
        #             ders_programlari = DersProgrami.objects.filter(saat=zaman[0], gun=zaman[1])
        #             _dersler.append([program.sube.ders for program in ders_programlari])
        #
        #     return _count, _dersler

    def bilgi_ver(self):
        msg = {
            "title": 'Ders Seçimi',
            "body": ' Ders seçiminiz kaydedilip danışmanıza gönderilmiştir.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Onay',
                                                        'body': 'Öğrencinin Ders Seçimlerini Onaylayınız'}

    def ogrenci_dersleri_onayla(self):
        _form = DersSecimForm(title="Ders Seçim Onayla", current=self.current)
        for sube_ders in self.current.task_data['sube_dersleri']:
            _form.Dersler(key=sube_ders['key'], ders_saati=sube_ders['ders_saati'], ders_gunu=sube_ders['ders_gunu'],
                          ders_tipi=sube_ders['ders_tipi'], ders_adi=sube_ders['ders_adi'])
        self.form_out(_form)

    def kontrol(self):
        if len(self.current.task_data['sube_dersleri']) > len(self.current.input['form']['Dersler']):
            self.current.task_data['cmd'] = 'ogrenci_bilgi_ver'
            self.current.task_data['degistirilen_dersler'] = self.current.input['form']['Dersler']
        else:
            self.current.task_data['cmd'] = 'ogrenci_derslerini_kaydet'

    def ogrenciye_bilgi_ver(self):
        msg = {
            "title": 'Ders Seçimi',
            "body": 'Seçilen derslerde yapılan değişiklik bilgisi öğrenciye aktarıldı.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['lane_change_invite'] = {'title': 'Ders Değişikliği',
                                                        'body': 'Danışmanınız tarafından dersleriniz değiştirilmiştir.'}

    def ogrenci_derslerini_kaydet(self):
        for sube_key in self.current.input['form']['Dersler']:
            sube = Sube.objects.get(sube_key['key'])
            ogrenci_dersi = OgrenciDersi()
            ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_key'])
            ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
            ogrenci_dersi.sube = sube
            ogrenci_dersi.ogrenci = ogrenci
            ogrenci_dersi.ogrenci_program = ogrenci_program
            ogrenci_dersi.save()
            ogrenci_dersi.delete()
            self.current.output['msgbox'] = {
                'type': 'info', "title": 'Mesaj Iletildi',
                "msg": 'Öğrencinin dersleri başarıyla kaydedilmiştir.'}

    def sube_secim_form_inline_edit(self):
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['type'] = 'model'
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['model_name'] = "Ders"
        self.output['forms']['schema']['properties']['Dersler']['quick_add'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add_field'] = "ders_adi"
        self.output['forms']['schema']['properties']['Dersler']['quick_add_view'] = "sube_arama"
