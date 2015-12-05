# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.

from zato.server.service import Service
from zato.common import DATA_FORMAT
import os
from time import sleep
import urllib2
import socket
from json import loads, dumps

os.environ["PYOKO_SETTINGS"] = 'ulakbus.settings'
from ulakbus.models.hitap import HizmetBirlestirme

H_USER = os.environ["HITAP_USER"]
H_PASS = os.environ["HITAP_PASS"]


class HizmetBirlestirmeSenkronizeEt(Service):
    """
    HITAP HizmetBirlestirmeSenkronizeEt Zato Servisi
    """

    def handle(self):

        def pass_hizmet_birlestirme(hizmet_birlestirme_passed, values):
            hizmet_birlestirme_passed.baslama_tarihi = values['baslama_tarihi']
            hizmet_birlestirme_passed.bitis_tarihi = values['bitis_tarihi']
            hizmet_birlestirme_passed.sgkNevi = values['sgkNevi']
            hizmet_birlestirme_passed.sgkSicilNo = values['sgkSicilNo']
            hizmet_birlestirme_passed.sure = values['sure']
            hizmet_birlestirme_passed.kamuIsyeriAd = values['kamuIsyeriAd']
            hizmet_birlestirme_passed.ozelIsyeriAd = values['ozelIsyeriAd']
            hizmet_birlestirme_passed.bagKurMeslek = values['bagKurMeslek']
            hizmet_birlestirme_passed.ulkeKod = values['ulkeKod']
            hizmet_birlestirme_passed.bankaSandikKod = values['bankaSandikKod']
            hizmet_birlestirme_passed.kidemTazminatOdemeDurumu = values['kidemTazminatOdemeDurumu']
            hizmet_birlestirme_passed.ayrilmaNedeni = values['ayrilmaNedeni']
            hizmet_birlestirme_passed.khaDurum = values['khaDurum']
            hizmet_birlestirme_passed.kurumOnayTarihi = values['kurumOnayTarihi']
            hizmet_birlestirme_passed.tckn = values['tckn']
            hizmet_birlestirme_passed.kayit_no = values['kayit_no']

            self.logger.info("hizmet_birlestirme successfully passed.")

        self.logger.info("zato service started to work.")

        tckn = self.request.payload['tckn']

        input_data = {'tckn': tckn}
        input_data = dumps(input_data)
        service_name = 'hizmet-birlestirme-getir.hizmet-birlestirme-getir'
        response = self.invoke(service_name, input_data, data_format=DATA_FORMAT.JSON, as_bunch=True)

        response_status = response["status"]
        if response_status == 'ok':
            hitap_dict = loads(response["result"])
            self.logger.info("hitap_dict created.")
        else:
            hitap_dict = {}
            self.logger.info("hitap_dict cannot created.")

        # if employee saved before, find that and add new records from hitap to riak
        try:
            local_records = {}
            # hizmet_birlestirme_list = HizmetBirlestirme.objects.filter(tckn=tckn)
            for record in HizmetBirlestirme.objects.filter(tckn=tckn):
                local_records[record.kayit_no] = {
                    'baslama_tarihi': record.baslama_tarihi,
                    'bitis_tarihi': record.bitis_tarihi,
                    'sgkNevi': record.sgkNevi,
                    'sgkSicilNo': record.sgkSicilNo,
                    'sure': record.sure,
                    'kamuIsyeriAd': record.kamuIsyeriAd,
                    'ozelIsyeriAd': record.ozelIsyeriAd,
                    'bagKurMeslek': record.bagKurMeslek,
                    'ulkeKod': record.ulkeKod,
                    'bankaSandikKod': record.bankaSandikKod,
                    'kidemTazminatOdemeDurumu': record.kidemTazminatOdemeDurumu,
                    'ayrilmaNedeni': record.ayrilmaNedeni,
                    'khaDurum': record.khaDurum,
                    'kurumOnayTarihi': record.kurumOnayTarihi,
                    'tckn': record.tckn,
                }

            # for k, v in local_records.iteritems():
            #     self.logger.info("Localdeki keyler => %s type %s" % (str(k), type(k)))

            # self.logger.info(local_records)
            self.logger.info("local_records created.")

            self.logger.info("Localdeki kayit sayisi: " + str(len(local_records)))
            self.logger.info("Hitaptan gelen kayit sayisi: " + str(len(hitap_dict)))

            '''
            for k, v in hitap_dict.items():
                if k not in local_records:
                    print "Bu kayit localde yok! => " + str(k)

            for k, v in local_records.items():
                if k not in hitap_dict:
                    print "Bu kayit hitapta yok! => " + str(k)
            '''

            # compare hitap incoming data and local db
            for hitap_key, hitap_values in hitap_dict.items():
                # self.logger.info("Hitap key: %s type %s" % (hitap_key, type(hitap_key)))
                if int(hitap_key) in local_records:
                    self.logger.info("hitap gelen data localde var.")
                    hizmet_birlestirme = HizmetBirlestirme.objects.filter(kayit_no=hitap_key).get()
                    if hizmet_birlestirme.sync == 1:
                        self.logger.info("hitaptan gelen data localde var ve senkronize.")
                    elif hizmet_birlestirme.sync == 2:
                        self.logger.info("hitap gelen data localde senkronize edildi.")
                        pass_hizmet_birlestirme(hizmet_birlestirme, hitap_values)
                        hizmet_birlestirme.sync = 1
                        hizmet_birlestirme.save()
                        # sleep(1.5)
                    else:
                        pass
                else:
                    self.logger.info("hitap gelen data localde yok. Kayit no => " + str(hitap_key))
                    hizmet_birlestirme = HizmetBirlestirme()
                    pass_hizmet_birlestirme(hizmet_birlestirme, hitap_values)
                    hizmet_birlestirme.sync = 1
                    hizmet_birlestirme.save()
                    # sleep(1.5)

            # compare local db and hitap incoming data
            for record_id, record_values in local_records.items():
                if unicode(record_id) not in hitap_dict:
                    hizmet_birlestirme = HizmetBirlestirme.objects.filter(kayit_no=record_id).get()
                    if hizmet_birlestirme.sync == 1:
                        hizmet_birlestirme.delete()
                        self.logger.info("localdeki sync data, hitapta yok, kayit no degismis olabilir, kayit silindi.")
                    else:
                        pass
                else:
                    if hizmet_birlestirme.sync != 1 or hizmet_birlestirme.sync != 2:
                        hizmet_birlestirme.delete()

                # hizmet_birlestirme.save()
            self.logger.info("Service runned.")

        # If not any record belongs to given tcno, create new one
        except IndexError:
            for hitap_keys, hitap_values in hitap_dict.items():
                hizmet_birlestirme = HizmetBirlestirme()
                pass_hizmet_birlestirme(hizmet_birlestirme, hitap_values)
                hizmet_birlestirme.sync = 1
                hizmet_birlestirme.save()
                self.logger.info("New HizmetBirlestirme saved.")
            # sleep(1)
        except socket.error:
            self.logger.info("Riak connection refused!")

        except AttributeError:
            self.logger.info("TCKN should be wrong!")
        except urllib2.URLError:
            self.logger.info("No internet connection!")

