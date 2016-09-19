# -*- coding:utf-8 -*-

from pyoko import Model, field
from zengine.lib.translation import gettext_lazy as _


class HitapSebep(Model):
    sebep_no = field.Integer(_(u"Sebep No"))
    ad = field.String(_(u"Sebep Adı"))
    nevi = field.Integer(_(u"Sebep Nevi"))
    zorunlu_alan = field.String(_(u"Zorunlu Alan"))

    class Meta:
        app = 'Personel'
        verbose_name = _(u"Hitap Sebep Kodu")
        verbose_name_plural = _(u"Hitap Sebep Kodları")
        list_fields = ['sebep_no', 'ad', 'nevi', 'zorunlu_alan']
        search_fields = ['sebep_no', 'ad']

    def __unicode__(self):
        return '%s - %s' % (self.sebep_no, self.ad)
