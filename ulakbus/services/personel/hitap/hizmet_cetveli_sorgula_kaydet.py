# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

__author__ = 'Ozgur Firat Cinar'

from zato.server.service import Service
import os
from time import sleep

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.personel import Employee

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetCetveliSorgula(Service):
    """
    HITAP HizmetCetveliSorgula Zato Servisi
    """

    def handle(self):

        def pass_service_records(employee, record_values):
            # if service_list[i].baslamaTarihi == '01.01.0001': service_list[i].baslamaTarihi = '22.05.1942'
            # service_records.start_date = service_list[i].baslamaTarihi
            # if service_list[i].bitisTarihi == '01.01.0001': service_list[i].bitisTarihi = '22.05.1942'
            # service_records.end_date = service_list[i].bitisTarihi
            service_records = employee.ServiceRecords()
            service_records.retirement_degree = record_values['emekliDerece']
            service_records.retirement_grade = record_values['emekliKademe']
            service_records.assignment = record_values['gorev']
            service_records.title_code = record_values['unvanKod']
            service_records.duty_class = record_values['hizmetSinifi']
            service_records.record_id = record_values['kayitNo']
            service_records.aquired_degree = record_values['kazanilmisHakAyligiDerece']
            service_records.aquired_grade = record_values['kazanilmisHakAyligiKademe']
            service_records.salary_degree = record_values['odemeDerece']
            service_records.salary_grade = record_values['odemeKademe']
            service_records.retirement_indicator = record_values['emekliEkGosterge']
            service_records.position_degree = record_values['kadroDerece']
            service_records.aquired_sup_indicator = record_values['kazanilmisHakAyligiEkGosterge']
            service_records.salary_sup_indicator = record_values['odemeEkGosterge']
            service_records.reason_code = record_values['sebepKod']
            service_records.pno = record_values['tckn']
            try:
                service_records.salary = float(record_values['ucret'].strip())
            except ValueError:
                pass
            try:
                service_records.wage = float(record_values['yevmiye'].strip())
            except ValueError:
                pass
            service_records.approval_date = record_values['kurumOnayTarihi']

            self.logger.info("Record saved successfully.")
            self.logger.info("RIAK KEY: %s " % employee.key)
            self.logger.info("kayitNo: %s " % service_records.record_id)

        tckn = self.request.payload['personel']['tckn']
        conn = self.outgoing.soap['HITAP'].conn

        # connects with soap client to the HITAP
        with conn.client() as client:
            service_bean = client.service.HizmetCetvelSorgula(H_USER, H_PASS, tckn).HizmetCetveliServisBean

        self.logger.info("zato service started to work.")

        # collects data from HITAP {record_id: record_values_belong_to_that_record_id}
        hitap_dict = {}
        for record in range(0, len(service_bean)):
            hitap_dict[service_bean[record].kayitNo] = {
                'baslamaTarihi': service_bean[record].baslamaTarihi,
                'bitisTarihi': service_bean[record].bitisTarihi,
                'emekliDerece': service_bean[record].emekliDerece,
                'emekliKademe': service_bean[record].emekliKademe,
                'gorev': service_bean[record].gorev,
                'unvanKod': service_bean[record].unvanKod,
                'hizmetSinifi': service_bean[record].hizmetSinifi,
                'kayitNo': service_bean[record].kayitNo,
                'kazanilmisHakAyligiDerece': service_bean[record].kazanilmisHakAyligiDerece,
                'kazanilmisHakAyligiKademe': service_bean[record].kazanilmisHakAyligiKademe,
                'odemeDerece': service_bean[record].odemeDerece,
                'odemeKademe': service_bean[record].odemeKademe,
                'emekliEkGosterge': service_bean[record].emekliEkGosterge,
                'kadroDerece': service_bean[record].kadroDerece,
                'kazanilmisHakAyligiEkGosterge': service_bean[record].kazanilmisHakAyligiEkGosterge,
                'odemeEkGosterge': service_bean[record].odemeEkGosterge,
                'sebepKod': service_bean[record].sebepKod,
                'tckn': service_bean[record].tckn,
                'ucret': service_bean[record].ucret,
                'yevmiye': service_bean[record].yevmiye,
                'kurumOnayTarihi': service_bean[record].kurumOnayTarihi
            }
        self.logger.info("hitap_dict created.")

        riak_dict_from_db_queries_with_pno = {}
        for record in Employee.objects.filter(pno=tckn).get().ServiceRecords:
            riak_dict_from_db_queries_with_pno[record.record_id] = {
                'baslamaTarihi': record.start_date,
                'bitisTarihi': record.end_date,
                'emekliDerece': record.retirement_degree,
                'emekliKademe': record.retirement_grade,
                'gorev': record.assignment,
                'unvanKod': record.title_code,
                'hizmetSinifi': record.duty_class,
                'kayitNo': record.record_id,
                'kazanilmisHakAyligiDerece': record.aquired_degree,
                'kazanilmisHakAyligiKademe': record.aquired_grade,
                'odemeDerece': record.salary_degree,
                'odemeKademe': record.salary_grade,
                'emekliEkGosterge': record.retirement_indicator,
                'kadroDerece': record.position_degree,
                'kazanilmisHakAyligiEkGosterge': record.aquired_sup_indicator,
                'odemeEkGosterge': record.salary_sup_indicator,
                'sebepKod': record.reason_code,
                'tckn': record.pno,
                'ucret': record.salary,
                'yevmiye': record.wage,
                'kurumOnayTarihi': record.approval_date
            }
        self.logger.info("riak_dict_from_db_queries_with_pno created.")

        # if employee saved before, find that and add new records from hitap to riak
        try:
            employee = Employee.objects.filter(pno=tckn)[0]
            for hitap_key, hitap_values in hitap_dict.items():
                if not riak_dict_from_db_queries_with_pno.has_key(hitap_key):
                    pass_service_records(employee, hitap_values)
                employee.save()

            # if any record exists in riak but not in hitap delete it
            for riak_dict_key, riak_dict_values in riak_dict_from_db_queries_with_pno.items():
                if not hitap_dict.has_key(riak_dict_key):
                    service_record_not_in_hitap_records = \
                    Employee.objects.filter(pno=tckn, service_records__record_id=riak_dict_key)[0].ServiceRecords[0]
                    service_record_not_in_hitap_records.remove()
                    self.logger.info("Deleted ")

        except IndexError:
            employee = Employee()
            employee.pno = tckn
            for record_id, record_values in hitap_dict.items():
                pass_service_records(employee, record_values)
                employee.save()
            sleep(1)
