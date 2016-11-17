# -*-  coding: utf-8 -*-
"""Form Modülü

Bu modül `Form` modeli ve bu modelle ilintili data modellerini içerir.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field
from zengine.lib.translation import gettext_lazy as _
from .auth import Role, Permission, User

__author__ = 'H.İbrahim Yılmaz (drlinux)'


class Form(Model):
    """Form Model sınıfı.

    Bu model, genel kullanım amaçlı olarak sisteme yüklenecek olan formların kayıt edileceği data
    modelidir.

    """
    ad = field.String(_(u"Form Adı"), index=True)
    file = field.File(_(u"File"), index=True,
                      random_name=True)  # form eger PDF olarak yulendiyse bu alan kullanilir.
    permissions = Permission()
    date = field.Date(_(u"Form Tarihi"), index=True, format="%d.%m.%Y")

    class Meta:
        app = 'Form'
        verbose_name = _(u"Form")
        verbose_name_plural = _(u"Formlar")
        list_fields = ['ad', 'date']
        search_fields = ['ad', 'file']

    def __unicode__(self):
        return '%s %s' % (self.ad, self.date)


class FormData(Model):
    """FormData Model sınıfı.

    Bu model, `Form` modelinde kayıtlı olan formlara ait dataların tutulacağı data modelidir.
    Veriler data field'ı içine json serialized olarak kayıt edilmektedir.

    """
    form = Form()
    data = field.Text(_(u"Form Data"), index=True)  # form datasi json serialized olarak saklanir
    user = User()
    role = Role()
    date = field.Date(_(u"Form Data Tarihi"), index=True, format="%d.%m.%Y")

    class Meta:
        app = 'Form'
        verbose_name = _(u"Form Data")
        verbose_name_plural = _(u"Form Data")
        list_fields = ['form', 'data', 'date']
        search_fields = ['data', 'date', 'user']

    def _form(self):
        return "%s" % self.form

    def __unicode__(self):
        return '%s %s' % (self.form, self.date)
