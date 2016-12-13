# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, format_time
from ulakbus.models.ders_sinav_programi import ZamanDilimleri
from collections import OrderedDict
from datetime import time


class ZamanDilimiDuzenle(CrudView):

    def varsayilan_zaman_dilimleri(self):
        zaman_dilimleri = sorted(ZamanDilimleri.objects.filter(birim=self.current.role.unit),
                                 key=lambda zd: zd.gun_dilimi)

        self.output['objects'] = [[_(u'Gün Dilimi'), _(u'Zaman Aralığı')]]
        for data in zaman_dilimleri:
            data_list = OrderedDict({})
            data_list["Gün Dilimi"] = "%s" % (data.get_gun_dilimi_display())
            data_list["Zaman Aralığı"] = "%(baslama)s-%(bitis)s" % {
                'baslama': format_time(time(int(data.baslama_saat), int(data.baslama_dakika))),
                'bitis': format_time(time(int(data.bitis_saat), int(data.bitis_dakika))),
            }
            item = {
                "title": _(u"Varsayılan Zaman Dilimleri"),
                'type': "table-multiRow",
                'fields': data_list,
                'actions': [
                    {'name': _(u'Değiştir'), 'cmd': 'degistir', 'show_as': 'button', 'object_key':'zaman_dilimi'}
                ],
                'key': data.key}
            self.output['objects'].append(item)

        _json = JsonForm(title=_(u"Güncel Zaman Dilimleri"))
        _json.tamamla = fields.Button(_(u"Bitir"), cmd='tamamla')
        self.form_out(_json)

    def zaman_dilimlerini_belirle(self):
        self.current.task_data['zaman_dilimi'] = self.current.input['zaman_dilimi']
        zd = ZamanDilimleri.objects.get(self.current.input['zaman_dilimi'])
        _json = JsonForm(title=_(u"ZAMAN DİLİMİ"))
        _json.gun_dilimi = fields.String(title=_(u"GÜN DİLİMİ"), default=zd.get_gun_dilimi_display())
        _json.baslangic_saat = fields.String(_(u"Başlangıç Saati"), default=zd.baslama_saat, required=False)
        _json.baslangic_dakika = fields.String(_(u"Başlangıç Dakikası"), default=zd.baslama_dakika, required=False)
        _json.bitis_saat = fields.String(_(u"Bitiş Saati"), default=zd.bitis_saat, required=False)
        _json.bitis_dakika = fields.String(_(u"Bitiş Dakikası"), default=zd.bitis_dakika, required=False)
        _json.kaydet = fields.Button(_(u"Kaydet"), cmd='kayit')
        _json.tamamlandi = fields.Button(_(u'İptal'), cmd='vazgec')
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
                   "title": _(u'Kaydedildi!'),
                   "msg": _(u"Kaydınız başarıyla gerçekleşti")}

            self.current.output['msgbox'] = msg
        except:
            msg = {"type": "warning",
                   "title": _(u'Kayıt Başarısız Oldu!'),
                   "msg": _(u"Malesef kaydınız başarısız oldu")}

            self.current.output['msgbox'] = msg

    def kayit_islemi_tamamlandi(self):
        msg = {"type": "info",
               "title": _(u'Kayıt İşleminiz Tamamlanmıştır!'),
               "msg": _(u'Güncel Zaman Dilimleri Zaman Tablosuna eklenmiştir')}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg
