# -*-  coding: utf-8 -*-
"""
Bu modul rapor veya formlari data kaynagi olarak kullanarak,
hedeflenen belge sablonlari bu datayi yerlestirerek belgeler
uretmeye yarayan belge ureteci modellerini kapsar.

Open Document Format standartlarina uygun belgeler uretilir.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from pyoko import Model, field

__author__ = 'Ali Riza Keles'


class DocGen(Model):
    """Document Generation Model

    """
    template = Template()
    data = field.File("Data")
    data_generation_date = field.DateTime("Data Generation Date", index=True, format="%d.%m.%Y")
    document = field.File("Generated Document")
    document_gen_date = field.File("Document Generation Date", index=True, format="%d.%m.%Y")
    origin = field.String("Origin")
    description = field.String("Description")

    class Meta:
        app = 'Document'
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        list_fields = ['description', 'document_gen_date']
        search_fields = ['document_gen_date']

    def __unicode__(self):
        return '%s %s' % (self.description, self.document_gen_date)


TEMPLATE_TYPES = [(1, "ODT"), (2, "ODS"), (3, "PLAIN TEXT"), (4, "HTML")]


class Template(Model):
    """Template Model.

    """
    template_type = field.Integer(choices=TEMPLATE_TYPES)
    template = field.File("Template")
    description = field.String("Description")
    preview = field.File("Preview")

    class Meta:
        app = 'Document'
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        list_fields = ['description']
        search_fields = ['description']

    def __unicode__(self):
        return '%s' % self.description
