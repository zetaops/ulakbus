# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models.ders_programi import GUN_DILIMI, ZamanDilimleri


class ZamanDilimiDuzenle(CrudView):

    def zaman_dilimlerini_belirle(self):
        _json = JsonForm(title="ZAMAN DİLİMİ")
        _json.gun_dilimi = fields.String("GÜN DİLİMİ", choices=GUN_DILIMI, default=1)
        _json.baslangic_saat = fields.String("Başlangıç Saati", required=False)
        _json.baslangic_dakika = fields.String("Başlangıç Dakikası", required=False)
        _json.bitis_saat = fields.String("Bitiş Saati", required=False)
        _json.bitis_dakika = fields.String("Bitiş Dakikası", required=False)
        _json.kaydet = fields.Button("Kaydet", cmd='kayit')
        _json.tamamlandi = fields.Button('Tamamla', cmd='bitir')

        self.form_out(_json)

    def kaydet(self):
        zd = ZamanDilimleri.objects.get(birim=self.current.role.unit,
                                        gun_dilimi=self.input['form']['gun_dilimi'])
        try:
            zd.baslama_saat = self.input['form']['baslangic_saat']
            zd.baslama_dakika = self.input['form']['baslangic_dakika']
            zd.bitis_saat = self.input['form']['bitis_saat']
            zd.bitis_dakika = self.input['form']['bitis_dakika']
            zd.save()

            msg = {"type": "info",
                   "title": 'Kaydedildi!',
                   "msg": "Kaydiniz basariyla gerceklesti"}

            self.current.output['msgbox'] = msg
        except:
            msg = {"type": "warning",
                   "title": 'Kayit Basarisiz Oldu!',
                   "msg": "Malesef kaydiniz basarisiz oldu"}

            self.current.output['msgbox'] = msg

    def kayit_islemi_tamamlandi(self):
        msg = {"type": "info",
               "title": 'Kayit Isleminiz Tamamlanmistir!',
               "msg": 'Guncel Zaman Dilimleri Zaman Tablosuna eklenmistir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg