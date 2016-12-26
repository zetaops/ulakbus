# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.ulakbus_service import UlakbusService
import json
import uuid
import httplib
import os

"""
UYARI : Lütfen bu kod içerisindeki uzun satırları formatlamayın. Gönderilen xml içersindeki
satırların bozulması durumunda kps tarafında HTTP_STATUS 400 dönmektedir.

"""

__author__ = 'Ali Riza Keles'

DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    import logging

    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


class NVIService(UlakbusService):

    HAS_CHANNEL = False

    def __init__(self):
        self.service_action = ""
        self.service_xml_body = ""
        self.sso_data = {}
        super(NVIService, self).__init__()

    def handle(self):
        keys = ['nvi_sso_encrypted_data', 'nvi_sso_key_identifier_path',
                'nvi_sso_digest_value', 'nvi_sso_signature',
                'nvi_sso_created', 'nvi_sso_expire']
        for k in keys:
            val = self.kvdb.conn.get(k)
            self.logger.info("k: %s, v: %s, type: %s" % (k, val, type(val)))
            self.sso_data.update({k: self.kvdb.conn.get(k)})
        if not all(self.sso_data.values()):
            self.invoke_sso_service()

        response = self.requestx()
        response_xml = response.read()
        self.response.payload = {"status": "ok" if response.status==200 else response.status, "result": self.xml_to_json(response_xml)}

    def invoke_sso_service(self):
        response = self.invoke('nvi-sts.sts-get-token')
        if response['status'] == 'ok':
            result = json.loads(response['result'])
            self.sso_data.update(result)
            # self.logger.info("DDDDDDDDDDDDD: %s" % result)
            # if response['status'] == 'ok':
            #     for k, v in result.items():
            #         self.sso_data.update({k, v})

    def request_xml(self):
        request_xml = """
        <?xml version="1.0"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
          <s:Header>
            <a:Action s:mustUnderstand="1">http://kps.nvi.gov.tr%s</a:Action>
            <a:MessageID>urn:uuid:%s</a:MessageID>
            <a:ReplyTo>
              <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
            </a:ReplyTo>
            <a:To s:mustUnderstand="1">https://kpsv2.nvi.gov.tr/Services/RoutingService.svc</a:To>
            <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
              <u:Timestamp u:Id="_0">
                <u:Created>%s</u:Created>
                <u:Expires>%s</u:Expires>
              </u:Timestamp>%s<Signature xmlns="http://www.w3.org/2000/09/xmldsig#">
                <SignedInfo>
                  <CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                  <SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"/>
                  <Reference URI="#_0">
                    <Transforms>
                      <Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"/>
                    </Transforms>
                    <DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"/>
                    <DigestValue>%s</DigestValue>
                  </Reference>
                </SignedInfo>
                <SignatureValue>%s</SignatureValue>
                <KeyInfo>
                  <o:SecurityTokenReference k:TokenType="http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV1.1" xmlns:k="http://docs.oasis-open.org/wss/oasis-wss-wssecurity-secext-1.1.xsd">
                    <o:KeyIdentifier ValueType="http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.0#SAMLAssertionID">%s</o:KeyIdentifier>
                  </o:SecurityTokenReference>
                </KeyInfo>
              </Signature>
            </o:Security>
          </s:Header>%s</s:Envelope>""" % (self.service_action, str(uuid.uuid1()), self.sso_data['nvi_sso_created'],
                                           self.sso_data['nvi_sso_expire'],
                                           self.sso_data['nvi_sso_encrypted_data'],
                                           self.sso_data['nvi_sso_digest_value'],
                                           self.sso_data['nvi_sso_signature'],
                                           self.sso_data['nvi_sso_key_identifier_path'],
                                           self.service_xml_body)
        return request_xml

    def requestx(self):
        request_xml = self.request_xml().replace('  ', '').replace('\n', '')
        self.logger.info("\n\n rxml: %s \n\n\n" % request_xml)
        conn = httplib.HTTPConnection("services.konya.edu.tr", 3128)
        headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
        conn.request("POST", "https://kpsv2.nvi.gov.tr/Services/RoutingService.svc",
                     request_xml, headers)
        return conn.getresponse()

    def xml_to_json(self, response_xml=None, response_element=None):
        from xml.dom import minidom
        response_dict = {}

        if response_xml:
            root = minidom.parseString(response_xml).getElementsByTagName('SorguSonucu')[0]
        else:
            root = response_element

        for e in root.childNodes:
            if e.hasChildNodes():
                response_dict[e.nodeName] = self.xml_to_json(response_element=e)
            elif e.nodeType == e.TEXT_NODE:
                return e.data

        return response_dict


class KisiSorgulaTCKimlikNo(NVIService):
    """
    NVI Kimlik Bilgileri Servisi
    """

    HAS_CHANNEL = True

    def handle(self):
        tckn = self.request.payload['tckn']
        self.service_action = "/2011/01/01/KisiSorgulaTCKimlikNoServis/ListeleCoklu"
        self.service_xml_body = """
            <env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://kps.nvi.gov.tr/2011/01/01">
                  <ns1:ListeleCoklu>
                      <ns1:kriterListesi>
                          <ns1:KisiSorgulaTCKimlikNoSorguKriteri>
                              <ns1:TCKimlikNo type="xsd:long">%s</ns1:TCKimlikNo>
                          </ns1:KisiSorgulaTCKimlikNoSorguKriteri>
                      </ns1:kriterListesi>
                  </ns1:ListeleCoklu>
            </env:Body>""" % tckn
        super(KisiSorgulaTCKimlikNo, self).handle()


class CuzdanSorgulaTCKimlikNo(NVIService):
    """
    NVI Kimlik Bilgileri Servisi
    """

    HAS_CHANNEL = True

    def handle(self):
        tckn = self.request.payload['tckn']
        self.service_action = "/2014/09/01/CuzdanSorgulaTCKimlikNoServis/ListeleCoklu"
        self.service_xml_body = """
            <env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://kps.nvi.gov.tr/2014/09/01">
                <ns1:ListeleCoklu>
                    <ns1:kriterListesi>
                        <ns1:CuzdanSorgulaTCKimlikNoSorguKriteri>
                            <ns1:CuzdanTur>Cuzdan</ns1:CuzdanTur>
                            <ns1:TCKimlikNo>%s</ns1:TCKimlikNo>
                        </ns1:CuzdanSorgulaTCKimlikNoSorguKriteri>
                    </ns1:kriterListesi>
                </ns1:ListeleCoklu>
            </env:Body>""" % tckn
        super(CuzdanSorgulaTCKimlikNo, self).handle()


class YabanciKisiSorgula(NVIService):
    """
    NVI Kimlik Bilgileri Servisi
    """

    HAS_CHANNEL = True

    def handle(self):
        tckn = self.request.payload['tckn']
        self.service_action = "/2013/06/01/YbKisiSorgulaYbKimlikNoServis/ListeleCoklu"
        self.service_xml_body = """
              <env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns2="http://kps.nvi.gov.tr/2013/06/01" xmlns:ns1="http://kps.nvi.gov.tr/2011/01/01">
                  <ns2:ListeleCoklu>
                      <ns2:kriterListesi>
                          <ns1:YbKisiSorgulaYbKimlikNoSorguKriteri>
                              <ns1:KimlikNo>%s</ns1:KimlikNo>
                          </ns1:YbKisiSorgulaYbKimlikNoSorguKriteri>
                      </ns2:kriterListesi>
                  </ns2:ListeleCoklu>
              </env:Body>""" % tckn
        super(YabanciKisiSorgula, self).handle()


class AdresSorgula(NVIService):
    """
    Adres Sorgulama
    """

    HAS_CHANNEL = True

    def handle(self):
        tckn = self.request.payload['tckn']
        self.service_action = "/2015/07/01/KimlikNoSorgulaAdresServis/Sorgula"
        self.service_xml_body = """
            <env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns2="http://kps.nvi.gov.tr/2015/07/01" xmlns:ns1="http://kps.nvi.gov.tr/2011/01/01">
                    <ns2:Sorgula>
                        <ns2:kriterListesi>
                            <ns1:KimlikNoileAdresSorguKriteri>
                                <ns1:KimlikNo>%s</ns1:KimlikNo>
                            </ns1:KimlikNoileAdresSorguKriteri>
                        </ns2:kriterListesi>
                    </ns2:Sorgula>
            </env:Body>""" % tckn
        super(AdresSorgula, self).handle()


class AileBireySorgula(NVIService):
    """
    Aile Birey Sorgulama
    """

    HAS_CHANNEL = True

    def handle(self):
        tckn = self.request.payload['tckn']
        self.service_action = "/2011/01/01/AileListesiAraTCNoServis/Sorgula"
        self.service_xml_body = """
            <env:Body xmlns:env="http://www.w3.org/2003/05/soap-envelope" xmlns:ns1="http://kps.nvi.gov.tr/2011/01/01">
                <ns1:Sorgula>
                    <ns1:kriterListesi>
                        <ns1:AileListesiAraTCNoSorguKriteri>
                            <ns1:KimlikNo>%s</ns1:KimlikNo>
                        </ns1:AileListesiAraTCNoSorguKriteri>
                    </ns1:kriterListesi>
                </ns1:Sorgula>
            </env:Body>""" % tckn

        super(AileBireySorgula, self).handle()
