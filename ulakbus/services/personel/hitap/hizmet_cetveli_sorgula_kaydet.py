# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
import sys
import os

sys.path.append('/opt/zato/external-py-lib/lib/python2.7/site-packages/')
sys.path.append('/opt/zato/external-py-lib/src/riak/')
os.environ["PYOKO_SETTINGS"] = 'zatoulakbus.settings'

from zatoulakbus.models.personel import Employee

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliSorgulaKaydet(Service):
    """
    Hitap'tan HizmetCetveliSorgula cagir donen verileri riak'a yaz
    """

    def handle(self):
        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        with conn.client() as client:
            service_list = client.service.HizmetCetvelSorgula(H_USER, H_PASS, tckn).HizmetCetveliServisBean

        em = Employee()
        em.pno = tckn

        sr = em.ServiceRecords()
        for i in range(0, len(service_list)):
            sr.start_date = service_list[i].baslamaTarihi if service_list[i].baslamaTarihi != '01.01.0001' else '22.05.1942'
            sr.end_date = service_list[i].bitisTarihi if service_list[i].bitisTarihi != '01.01.0001' else '22.05.1942'
            sr.retirement_degree = service_list[i].emekliDerece
            sr.retirement_grade = service_list[i].emekliKademe
            sr.assignment = service_list[i].gorev
            sr.title_code = service_list[i].unvanKod
            sr.duty_class = service_list[i].hizmetSinifi
            sr.record_id = service_list[i].kayitNo
            sr.aquired_degree = service_list[i].kazanilmisHakAyligiDerece
            sr.aquired_grade = service_list[i].kazanilmisHakAyligiKademe
            sr.salary_degree = service_list[i].odemeDerece
            sr.salary_grade = service_list[i].odemeKademe
            sr.retirement_indicator = service_list[i].emekliEkGosterge
            sr.position_degree = service_list[i].kadroDerece
            sr.aquired_sup_indicator = service_list[i].kazanilmisHakAyligiEkGosterge
            sr.salary_sup_indicator = service_list[i].odemeEkGosterge
            sr.reason_code = service_list[i].sebepKod
            sr.pno = service_list[i].tckn
            sr.salary = service_list[i].ucret
            sr.wage = service_list[i].yevmiye
            sr.approval_date = service_list[i].kurumOnayTarihi

        em.save()

        self.logger.info("Employee saved successfully.")
        self.logger.info("Employee key: %s " % em.key)
