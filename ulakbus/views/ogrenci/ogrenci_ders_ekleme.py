# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Ogrenci, OgrenciDersi, Program, OgrenciProgram, Ders, Donem, Sube, DersProgrami
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView


# def sube_arama(current):
#     q = current.input.get('query')
#     r = []
#
#     for o in Sube.objects.search_on(*['ders_adi'], contains=q):
#         r.append((o.key, o.__unicode__()))
#
#     current.output['objects'] = r


class DersSecimForm(JsonForm):
    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')
        ders_saati = fields.Integer('Ders Saati')
        ders_gunu = fields.String('Ders Günü')
        ders_tipi = fields.String('Ders Tipi')

    ileri = fields.Button("İleri")


class OgrenciDersEkleme(CrudView):
    class Meta:
        model = 'Ders'

    @staticmethod
    def basarisiz_ogrenci_dersleri_bul(ogrenci):
        eski_donem_ogrenci_dersleri = []
        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], contains='F').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)

        basarisiz_ogrenci_dersleri = OgrenciDersi.objects.search_on(*['harflendirilmis_not'], startswith='DD').filter(
            ogrenci=ogrenci)
        eski_donem_ogrenci_dersleri.extend(basarisiz_ogrenci_dersleri)
        return [ogrenci_dersi.sube.ders.kod for ogrenci_dersi in eski_donem_ogrenci_dersleri]

    @staticmethod
    def yeni_donem_acilan_basarisiz_dersleri_bul(ogrenci_program):
        yeni_donem_basarisiz_dersler = []
        eski_donem_ders_kodlari = OgrenciDersEkleme.basarisiz_ogrenci_dersleri_bul(ogrenci_program.ogrenci)
        for ders_kodu in eski_donem_ders_kodlari:
            try:
                ders = Ders.objects.get(kod=ders_kodu, donem=Donem.guncel_donem(), program=ogrenci_program.program)
                yeni_donem_basarisiz_dersler.append(ders)
            except ObjectDoesNotExist:
                dersler = Ders.objects.filter(kod=ders_kodu)
                for ders in dersler:
                    try:
                        if not ders.donem.guncel:
                            yerine_ders = Ders.objects.get(yerine_ders=ders, donem=Donem.guncel_donem(),
                                                           program=ogrenci_program.program)
                            yeni_donem_basarisiz_dersler.append(yerine_ders)
                    except ObjectDoesNotExist:
                        pass
        return OgrenciDersEkleme.yeni_donem_dersleri_bul(ogrenci_program, yeni_donem_basarisiz_dersler)

    @staticmethod
    def yeni_donem_dersleri_bul(ogrenci_program, yeni_donem_basarisiz_dersler):
        programa_kayitli_zorunlu_dersler = Ders.objects.filter(program=ogrenci_program.program,
                                                               donem=Donem.guncel_donem(),
                                                               zorunlu=True)
        yeni_donem_ders_kodlari = [ders.kod for ders in yeni_donem_basarisiz_dersler]
        for zorunlu_ders in programa_kayitli_zorunlu_dersler:
            if zorunlu_ders.kod not in yeni_donem_ders_kodlari:
                yeni_donem_basarisiz_dersler.append(zorunlu_ders)
        return yeni_donem_basarisiz_dersler

    def ogrenci_ders_secme(self):
        """
        Subeye saat ve gün fieldları ekelnecek, seçmeli derslerden zorunlu olanlarda eklencek.
        Yeni dönem ait program dersleri listeleneck şubleriyle beraber.

        :return:
        """
        p = Program.objects.get(birim=self.current.role.unit)
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.current.task_data['ogrenci_key'] = ogrenci.key
        ogrenci_program = OgrenciProgram.objects.get(program=p, ogrenci=ogrenci)
        self.current.task_data['ogrenci_program_key'] = ogrenci_program.key
        kredi = []
        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        yeni_donem_dersler = OgrenciDersEkleme.yeni_donem_acilan_basarisiz_dersleri_bul(ogrenci_program)
        for ders in yeni_donem_dersler:
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
                                 _ders.secmeli_tekrar]
                    kredi.extend([_ders.yerel_kredisi for _ders in ders_list])
                    sube_list = [_ders.sube_set for _ders in ders_list]
                    for sube in sube_list[0]:
                        for ders_programi in sube.sube.ders_programi_set:
                            _form.Dersler(key=sube.sube.key, ders_adi=sube.sube.ders_adi,
                                          ders_saati=ders_programi.ders_programi.saat,
                                          ders_gunu=ders_programi.ders_programi.gun,
                                          ders_tipi=secmeli_ders.secmeli_ders_gruplari.secmeli_grup_adi)
            if 'cakisan_ders_bilgileri' in self.current.task_data:
                _form.help_text = 'Maximum kredi {} ,seçilen derslerin toplam kredisi {},' \
                                  ' minimum kredi {} , kalan krediniz {}dir.{}' \
                    .format(45, sum(kredi), 30, 45 - sum(kredi), self.current.task_data['cakisan_ders_bilgileri'])
            elif 'ayni_ders_bilgileri' in self.current.task_data:
                _form.help_text = 'Maximum kredi {} ,seçilen derslerin toplam kredisi {},' \
                                  ' minimum kredi {} , kalan krediniz {}.{}' \
                    .format(45, sum(kredi), 30, 45 - sum(kredi), self.current.task_data['ayni_ders_bilgileri'])
            elif 'ayni_ders_bilgileri' and 'cakisan_ders_bilgileri' in self.current.task_data:
                _form.help_text = 'Maximum kredi {} ,seçilen derslerin toplam kredisi {},' \
                                  ' minimum kredi {} , kalan krediniz {}.{}, {}' \
                    .format(45, sum(kredi), 30, 45 - sum(kredi), self.current.task_data['ayni_ders_bilgileri'],
                            self.current.task_data['cakisan_ders_bilgileri'])
            else:
                _form.help_text = 'Maximum kredi {} ,seçilen derslerin toplam kredisi {},' \
                                  ' minimum kredi {}, kalan krediniz {}' \
                    .format(45, sum(kredi), 30, 45 - sum(kredi))
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = True

    @staticmethod
    def ders_zamani_kredisi_keyleri_bul(subeler):
        derslerin_keyleri = []
        derslerin_kredileri = []
        derslerin_zamanlari = []
        for item in subeler:
            sube = Sube.objects.get(item['key'])
            derslerin_keyleri.append(sube.ders.key)
            derslerin_kredileri.append(sube.ders.yerel_kredisi)
            # listten kurtar gereksiz
            derslerin_zamanlari.append((item['ders_saati'], item['ders_gunu']))
        return derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari

    @staticmethod
    def cakisan_dersleri_bul(derslerin_zamanlari):
        count = 0
        for i in range(len(derslerin_zamanlari)):
            if derslerin_zamanlari.count(derslerin_zamanlari[i]) > 1:
                count = derslerin_zamanlari.count(derslerin_zamanlari[i])
        _dersler = []
        for zaman in set(derslerin_zamanlari):
            _count = derslerin_zamanlari.count(zaman)
            if _count > 1:
                ders_programlari = DersProgrami.objects.filter(saat=zaman[0], gun=zaman[1])
                _dersler.append([program.sube.ders for program in ders_programlari])
        return count, _dersler

    @staticmethod
    def ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri):
        d_key = {}
        for ders_key in derslerin_keyleri:
            if ders_key in d_key:
                d_key[ders_key] += 1
            else:
                d_key[ders_key] = 1
        return d_key

    def ders_secimlerini_kontrol_et(self):
        self.current.task_data['sube_dersleri'] = self.current.input['form']['Dersler']
        derslerin_keyleri, derslerin_kredileri, derslerin_zamanlari = \
            OgrenciDersEkleme.ders_zamani_kredisi_keyleri_bul(self.current.input['form']['Dersler'])
        self.current.task_data['kredi'] = sum(derslerin_kredileri)
        count, cakisan_dersler = OgrenciDersEkleme.cakisan_dersleri_bul(derslerin_zamanlari)
        self.current.task_data['cakisan_ders_bilgileri'] = "%s dersleri çakışmaktadır" % cakisan_dersler
        d_key = OgrenciDersEkleme.ayni_derse_ait_birden_fazla_subenin_keylerini_bul(derslerin_keyleri)
        for key in d_key:
            if d_key[key] > 1:
                ders = Ders.objects.get(d_key)
                self.current.task_data[
                    'ayni_ders_bilgileri'] = "%s dersine ait %s şube seçtiniz,1 tane şube seçiniz" % (ders, d_key[key])
            if d_key[key] > 1 or count:
                self.current.task_data['ders_secim_command'] = 'ogrenci_ders_secim'
                break
            else:
                self.current.task_data['cmd'] = 'ogrenci_dersi_kaydet'

    def ogrenci_dersi_kaydet(self):
        for sube_key in self.current.task_data['sube_dersleri']:
            sube = Sube.objects.get(sube_key['key'])
            ogrenci_dersi = OgrenciDersi()
            ogrenci = Ogrenci.objects.get(self.current.task_data['ogrenci_key'])
            ogrenci_program = OgrenciProgram.objects.get(self.current.task_data['ogrenci_program_key'])
            ogrenci_dersi.sube = sube
            ogrenci_dersi.ogrenci = ogrenci
            ogrenci_dersi.ogrenci_program = ogrenci_program
            ogrenci_dersi.save()
            ogrenci_dersi.delete()
        msg = {
            'type': 'info', "title": 'Ders Seçimi',
            "msg": ' Ders seçimi başarıyla kaydedilmiştir.'}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def ogrenci_dersleri_onayla(self):
        pass
