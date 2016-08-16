# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models.ders_sinav_programi import GUN_DILIMI, ZamanDilimleri
from collections import OrderedDict


class ZamanDilimiDuzenle(CrudView):

    def varsayilan_zaman_dilimleri(self):
        zaman_dilimleri = sorted(ZamanDilimleri.objects.filter(birim=self.current.role.unit),
                                 key=lambda zd: zd.gun_dilimi)

        self.output['objects'] = [['Gün Dilimi', 'Zaman Aralığı']]
        for data in zaman_dilimleri:
            data_list = OrderedDict({})
            data_list["Gün Dilimi"] = "%s" % (data.get_gun_dilimi_display())
            data_list["Zaman Aralığı"] = "%s:%s-%s:%s" % (data.baslama_saat,
                                                          data.baslama_dakika,
                                                          data.bitis_saat,
                                                          data.bitis_dakika)
            item = {
                "title": "Default Zaman Dilimleri",
                'type': "table-multiRow",
                'fields': data_list,
                'actions': [
                    {'name': 'Değiştir', 'cmd': 'degistir', 'show_as': 'button', 'object_key':'zaman_dilimi'}
                ],
                'key': data.key}
            self.output['objects'].append(item)

        _json = JsonForm(title="Güncel Zaman Dilimleri")
        _json.tamamla = fields.Button("Bitir", cmd='tamamla')
        self.form_out(_json)

    def zaman_dilimlerini_belirle(self):
        self.current.task_data['zaman_dilimi'] = self.current.input['zaman_dilimi']
        zd = ZamanDilimleri.objects.get(self.current.input['zaman_dilimi'])
        _json = JsonForm(title="ZAMAN DİLİMİ")
        _json.gun_dilimi = fields.String(title="GÜN DİLİMİ", default=zd.get_gun_dilimi_display())
        _json.baslangic_saat = fields.String("Başlangıç Saati", default=zd.baslama_saat, required=False)
        _json.baslangic_dakika = fields.String("Başlangıç Dakikası", default=zd.baslama_dakika, required=False)
        _json.bitis_saat = fields.String("Bitiş Saati", default=zd.bitis_saat, required=False)
        _json.bitis_dakika = fields.String("Bitiş Dakikası", default=zd.bitis_dakika, required=False)
        _json.kaydet = fields.Button("Kaydet", cmd='kayit')
        _json.tamamlandi = fields.Button('İptal', cmd='vazgec')
        self.form_out(_json)

    def kaydet(self):
        zd = ZamanDilimleri.objects.get(self.current.task_data['zaman_dilimi'])
        try:
            zd.baslama_saat = self.input['form']['baslangic_saat']
            zd.baslama_dakika = self.input['form']['baslangic_dakika']
            zd.bitis_saat = self.input['form']['bitis_saat']
            zd.bitis_dakika = self.input['form']['bitis_dakika']
            zd.save()

            msg = {"type": "info",
                   "title": 'Kaydedildi!',
                   "msg": "Kaydınız başarıyla gerçekleşti"}

            self.current.output['msgbox'] = msg
        except:
            msg = {"type": "warning",
                   "title": 'Kayit Basarisiz Oldu!',
                   "msg": "Malesef kaydiniz basarisiz oldu"}

            self.current.output['msgbox'] = msg

    def kayit_islemi_tamamlandi(self):
        msg = {"type": "info",
               "title": 'Kayıt İşleminiz Tamamlanmıştır!',
               "msg": 'Guncel Zaman Dilimleri Zaman Tablosuna eklenmistir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg