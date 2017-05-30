# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import time

from zato.server.service import Service
from ulakbus.models.zato import ZatoServiceChannel, ZatoServiceFile


class ServiceManagement(Service):

    """
        Eğer yerelde çalışıyorsanız zato ortamına http://localhost:8183/ adresini vererek
        bağlanabirlisiniz.

        Service Management Zato'ya yüklenecek servisdir. Zato'ya herhangi bir servis
        yükleme işlemi ise;
        Services -> List services -> Upload a service package  diyerek servisin bulunduğu
        klasör seçilir ve işlem tamamlanır.

        Servisi yükledikten sonra projemizde bulunan diger servisleri otomatik yüklemek ve
        onlara bağlı kanalları yaratmak için yüklediğimiz servise bağlı bir kanal yaratmamız
        lazım bu işlemi ise;
        Connections -> Channels -> Plain HTTP -> Create a new Plain HTTP channel  işlemleri
        yapılarak yeni kanal yaratma formu gelir.

            #Name:                      deploy ulakbus services (Farklı bir isim olabilir)
            #URL path:                  /deploy-ulakbus-services (Farklı url ismi olabilir)
            #Data format:               JSON (zorunlu)
            #Service:                   Service Management (get_name methodunda return edilen değer)
            #Security definition:       No security definition (zorunlu)

            seçenekleri seçilip kanal yaratma işlemi tamamlanır.

        Kanal yaratıldıktan sonra manage.py load_zato_services --path services/ komutunu
        çalıştırdığımız zaman services klasörü altında bulunan butun servisler için ZatoServiceFile
        ve ZatoServiceChannel modellerini dolduracak.

        Modelleri doldurduktan sonra artık servislerimizi Zato'ya yükleyebiliriz.
        Bu işlemi gerçekleştirmek için ise;

        curl localhost:11223/deploy-ulakbus-services

        dememiz yeterli olacaktir. Yukleme islemi tamamlandıktan sonra servisleri test edip,
        kullanabilirsiniz.

    """

    @staticmethod
    def get_name():
        return "Service Management"

    def handle(self):
        """
            İlk olarak servislerin bulunduğu python dosyalarını zatoya yükleme işlemi
            gerçekleştirilir.

                ZatoServiceFile.objects.filter(deploy=False) burada zatoya yüklenmemiş objeleri
                çağırıyoruz.

                Yüklenmemiş objeleri zatonun bize sağlamış olduğu api sayesinde;

                    self.invoke('zato.service.upload-package', payload={..})

                servisleri zatoya yüklüyoruz. Gönderdikten sonra objeyi
                deploy=True yapıp kaydediyoruz.

            Servisleri zatoya yükleme işlemi gerçekleştikten sonra kanalları yaratabilriz.

                ZatoServiceChannel.objects.filter(deploy=False) bu sorguda ise zatoya
                yuklenecek kanal objelerini çağırıyoruz.

                self.invoke('zato.service.get-by-name', payload={..}) -> zatoya yüklenen

                kanala ait servislerin idlerine ulaşmak için bu sorguyu yapıyoruz. Dönen
                responsedan kanalın id'sini modele kaydediyoruz.

                self.invoke('zato.http-soap.create', payload={..}) -> zatoda ilgili servise

                bağlı kanal oluşturur.

        """
        ulakbus_service_files = ZatoServiceFile.objects.filter(deploy=False)
        if ulakbus_service_files:
            for ulakbus_service_file in ulakbus_service_files:

                self.invoke(
                        'zato.service.upload-package',
                        payload={"cluster_id": ulakbus_service_file.cluster_id,
                                 "payload_name": ulakbus_service_file.service_payload_name,
                                 "payload": ulakbus_service_file.service_payload})
                ulakbus_service_file.deploy = True
                ulakbus_service_file.save()
                time.sleep(0.3)

        ulakbus_channels = ZatoServiceChannel.objects.filter(deploy=False)

        if ulakbus_channels:
            for ulakbus_channel in ulakbus_channels:
                resp_service_name = self.invoke('zato.service.get-by-name',
                                                payload={
                                                    "cluster_id": 1,
                                                    "name": ulakbus_channel.service_name})
                time.sleep(0.3)
                ulakbus_channel.service_id = resp_service_name['zato_service_get_by_name_response']['id']

                resp_channel = self.invoke(
                    'zato.http-soap.create',
                    payload={"cluster_id": ulakbus_channel.cluster_id,
                             "name": ulakbus_channel.channel_name,
                             "is_active": ulakbus_channel.channel_is_active,
                             "connection": ulakbus_channel.channel_connection,
                             "transport": ulakbus_channel.channel_transport,
                             "is_internal": ulakbus_channel.channel_is_internal,
                             "url_path": ulakbus_channel.channel_url_path,
                             "data_format": ulakbus_channel.channel_data_format,
                             "service": ulakbus_channel.service_name})
                ulakbus_channel.channel_id = resp_channel['zato_http_soap_create_response']['id']

                ulakbus_channel.deploy = True
                ulakbus_channel.save()
                time.sleep(0.3)
