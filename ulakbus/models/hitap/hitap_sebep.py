# -*- coding:utf-8 -*-

from pyoko import Model, field


class HitapSebep(Model):
    sebep_no = field.Integer("Sebep No")
    ad = field.String("Sebep Adı")
    nevi = field.Integer("Sebep Nevi")
    zorunlu_alan = field.String("Zorunlu ALan")

    class Meta:
        app = 'Personel'
        verbose_name = "Hitap Sebep Kodu"
        verbose_name_plural = "Hitap Sebep Kodları"
        list_fields = ['sebep_no', 'ad', 'nevi', 'zorunlu_alan']
        search_fields = ['sebep_no', 'ad']

    def __unicode__(self):
        return '%s - %s' % (self.sebep_no, self.ad)
