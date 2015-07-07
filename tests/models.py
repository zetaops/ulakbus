# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.model import Model, ListNode, Node
from pyoko import field


class Employee(Model):

    first_name = field.String("Adı", index=True)
    last_name = field.String("Soyadı", index=True)
    staff_type = field.String("Personel Türü", index=True)
    birth_date = field.Date("Doğum Tarihi", index=True, default='')

    class ServiceRecords(ListNode):
        start_date = field.Date("Başlangıç Tarihi", index=True)
        end_date = field.Date("Bitiş Tarihi", index=True)
        retirement_degree = field.Integer("Emeklilik Derece", index=True)
        retirement_grade = field.Integer("Emeklilik Kademe", index=True)
        assignment = field.String("Görev", index_as='text_tr')
        title_code = field.Integer("Ünvan Kodu", index=True)
        duty_class = field.String("Hizmet Sınıfı", index_as=True)
        record_id = field.Integer("Kayıt No", index=True)
        aquired_degree = field.Integer("Kazanılmış Hak Aylığı Derece", index=True)
        aquired_grade = field.Integer("Kazanılmış Hak Aylığı Kademe", index=True)
        salary_degree = field.Integer("Ödemeye Esas Derece", index=True)
        salary_grade = field.Integer("Ödemeye Esas Kademe", index=True)
        retirement_indicator = field.Integer("Emeklilik Gösterge", index=True)
        position_degree = field.String("Kadro Derece", index_as='text_tr')
        aquired_sup_indicator = field.Integer("Kazanılmış Hak Aylığı Ek gösterge", index=True)
        salary_sup_indicator = field.Integer("Ödeme Ek Gösterge", index=True)
        reason_code = field.Integer("Sebep Kodu", index=True)
        pno = field.Integer("TC No", index=True)
        salary = field.Float("Ücret", index=True)
        wage = field.Float("Yemiye", index_as=True)
        approval_date = field.Date("Kurum Onay Tarihi", index=True)

