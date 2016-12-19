# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


__author__ = 'Ali Riza Keles'

from ulakbus.services.ulakbus_service import UlakbusService
import os
import httplib
import xml.etree.ElementTree as ET
import base64
import hashlib
import hmac
import datetime
import json
import uuid

DEBUG = os.environ.get('DEBUG', False)
if DEBUG:
    import logging

    httplib.HTTPConnection.debuglevel = 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


class STSGetToken(UlakbusService):
    """
    NVI STS SSO Token
    """

    HAS_CHANNEL = True

    def handle(self):
        # tckn = self.request.payload['tckn']

        created = datetime.datetime.now().isoformat()
        expire = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
        username = os.environ["NVI_USER"]
        password = os.environ["NVI_PASS"]

        sts_request = """
            <s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing" xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">
              <s:Header>
                <a:Action s:mustUnderstand="1">http://docs.oasis-open.org/ws-sx/ws-trust/200512/RST/Issue</a:Action>
                <a:MessageID>urn:uuid:%s</a:MessageID>
                <a:ReplyTo>
                  <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
                </a:ReplyTo>
                <a:To s:mustUnderstand="1">https://kimlikdogrulama.nvi.gov.tr/services/issuer.svc/IWSTrust13</a:To>
                <o:Security s:mustUnderstand="1" xmlns:o="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
                  <u:Timestamp u:Id="_0">
                    <u:Created>%s</u:Created>
                    <u:Expires>%s</u:Expires>
                  </u:Timestamp>
                  <o:UsernameToken u:Id="uuid-a388cb10-46ab-48e5-9890-5103cc3dd20b-1">
                    <o:Username>%s</o:Username>
                    <o:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">%s</o:Password>
                  </o:UsernameToken>
                </o:Security>
              </s:Header>
              <s:Body>
                <trust:RequestSecurityToken xmlns:trust="http://docs.oasis-open.org/ws-sx/ws-trust/200512">
                  <wsp:AppliesTo xmlns:wsp="http://schemas.xmlsoap.org/ws/2004/09/policy">
                    <a:EndpointReference>
                      <a:Address>https://kpsv2.nvi.gov.tr/services/RoutingService.svc</a:Address>
                    </a:EndpointReference>
                  </wsp:AppliesTo>
                  <trust:RequestType>http://docs.oasis-open.org/ws-sx/ws-trust/200512/Issue</trust:RequestType>
                </trust:RequestSecurityToken>
              </s:Body>
            </s:Envelope>
        """ % (str(uuid.uuid1()), str(created), str(expire), username, password)

        conn = httplib.HTTPConnection("services.konya.edu.tr", 3128)
        headers = {"Content-Type": "application/soap+xml; charset=utf-8"}
        conn.request("POST", "https://kimlikdogrulama.nvi.gov.tr/Services/Issuer.svc/IWSTrust13", sts_request, headers)

        response = conn.getresponse()
        sts_response = response.read()
        root = ET.fromstring(sts_response)
        created = datetime.datetime.now().isoformat()
        expire = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()

        encrypted = root.find(
            '{http://www.w3.org/2003/05/soap-envelope}Body/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponseCollection/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponse/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestedSecurityToken/*')
        encrypted_data = ET.tostring(encrypted)

        key_identifier_path = root.find(
            '{http://www.w3.org/2003/05/soap-envelope}Body/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponseCollection/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponse/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestedUnattachedReference/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}SecurityTokenReference/{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}KeyIdentifier').text

        binary_secret = root.find(
            '{http://www.w3.org/2003/05/soap-envelope}Body/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponseCollection/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestSecurityTokenResponse/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}RequestedProofToken/{http://docs.oasis-open.org/ws-sx/ws-trust/200512}BinarySecret').text

        digest_value = base64.b64encode(hashlib.sha1(
            '<u:Timestamp xmlns:u="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" u:Id="_0"><u:Created>' + created + '</u:Created><u:Expires>' + expire + '</u:Expires></u:Timestamp>').digest())

        signature = base64.b64encode(hmac.new(base64.b64decode(binary_secret),
                                              '<SignedInfo xmlns="http://www.w3.org/2000/09/xmldsig#"><CanonicalizationMethod Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></CanonicalizationMethod><SignatureMethod Algorithm="http://www.w3.org/2000/09/xmldsig#hmac-sha1"></SignatureMethod><Reference URI="#_0"><Transforms><Transform Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"></Transform></Transforms><DigestMethod Algorithm="http://www.w3.org/2000/09/xmldsig#sha1"></DigestMethod><DigestValue>' + digest_value + '</DigestValue></Reference></SignedInfo>',
                                              hashlib.sha1).digest())

        result = {
            "nvi_sso_encrypted_data": encrypted_data,
            "nvi_sso_digest_value": digest_value,
            "nvi_sso_signature": signature,
            "nvi_sso_key_identifier_path": key_identifier_path,
            "nvi_sso_created": created,
            "nvi_sso_expire": expire
        }

        for k, v in result.iteritems():
            # save nvi sso data into redis for `3600` seconds
            self.kvdb.conn.set(k, v)
            self.kvdb.conn.expire(k, 600)

        if DEBUG:
            self.logger.info("NVI SSO invoked: %s" % json.dumps(result))

        self.response.payload = {"status": "ok", "result": json.dumps(result)}