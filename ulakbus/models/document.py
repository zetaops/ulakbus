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
from ulakbus.lib.s3_file_manager import S3FileManager

__author__ = 'Ali Riza Keles'

TEMPLATE_TYPES = [(1, "ODT"), (2, "ODS"), (3, "PLAIN TEXT"), (4, "HTML")]


class Template(Model):
    """Template Model.

    """

    template_type = field.Integer(choices=TEMPLATE_TYPES)
    template = field.File(random_name="Template")
    description = field.String("Description")
    preview = field.File(random_name="Preview")
    version = field.String("Version")
    modify_date = field.DateTime("ModifyDate", format='%d %b %Y %H:%M:%S')
    name = field.String("Name", unique=True)

    def post_save(self):
        """
        Get last_modified from S3 and update modify_date of this object.
        Returns:

        """
        s3_manager = S3FileManager()
        s3_time = s3_manager.get_last_modified_date(self.template)

        modify_date = self.change_date_format(s3_time)
        self.modify_date = modify_date

        self.save(internal=True)

    @staticmethod
    def change_date_format(s3_modify_date):
        """
        Change date time format for model.
        Args:
            s3_modify_date: <str>

        Returns: Formatted date time in str. <str>

        """
        s3_time = s3_modify_date.split(" ")[1:-1]
        cut_time = '{} {} {} {}'.format(s3_time[0], s3_time[1], s3_time[2], s3_time[3])
        return cut_time

    class Meta:
        app = 'Document'
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        list_fields = ['description']
        search_fields = ['description']

    def __unicode__(self):
        return '%s' % self.description
