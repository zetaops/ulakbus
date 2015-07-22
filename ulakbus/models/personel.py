# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.model import Model, ListNode, Node
from pyoko import field
"""
ad	name
soyad	surname
dogum_tarih	birth_date
dogum_yer	birth_place
mahalle_koy	neighborhood
baba_ad	father_name
ana_ad	mother_name
cinsiyet	gender
medeni_hal	marital_status
ilce_kod	town_code
il_kod	city
kan_grup	blood_type
onceki_soyad	former_surname
ev_telefon	home_phone
is_telefon	work_phone
cep_telefon	mobile_phone
adress1	address1
adress2	address2
posta_kod	postal_code
eposta1	primary_email
eposta2	secondary_email
web_sayfa	web
sicil_no	registry_code
statu_kod	status_code
hizmet_sinif_kod	labour_class_code
saglik_durum	health_status
ozurlu_derece	degree_of_disabled
vergi_no	tax_no
parola	password
arsiv	archive
emekli_sicil_no	retirement_no
emekli_giris_tarih	retirement_start_date
adres_il_kod	address_city_code
adres_ilce_kod	address_town_code
ulke_kod	country_code
min_derece	min_degree
min_kademe	min_grade
cilt_no	volume_no
aile_sira_no	family_serial_no
sira_no	item_no
kimlik_seri	identity_serial_no
kimlik_no	identity_no
kimlik_veren_yer	place_of_identity_given
kimlik_verilis_neden	identity_delivery_reason
kimlik_kayit_no	identity_registry_no
kimlik_verilis_tarihi	identity_date_of_issue
adaylik	nomination
goreve_baslama_tarihi	assignment_start_date
gorev_bitis_tarihi	assignment_end_date
kontrol	control
tag1	tag1
tag2
tag3
personel_tip	staff_type
terfi_aciklama	promotion_desc
gorev_aciklama	task_desc
terfi_ceza	promotion_penalty
terfi_asker	promotion_military_service
terfi_ucretsiz	promotion_unpaid
terfi_sicil	promotion_registry
gorev_uzatma	duty_time_extension
brans	branch
terfi_bakanlik_gelen	promotion_order_ministry
is_adres	work_address
notlar	notes
ek_gosterge	additional_indicator
ozur_grup_kod	disabled_group_code
ozur_oran	disabled_ratio
hitap_id	hitap_id
gon
hitap_hata_kod	hitap_error_code
hitap_hata_mesaj	hitap_error_message
anket	survey
ozluk_sebep	registry_reason
hitap_gonderme_tarih	hitap_request_departure_date
hitap_ack	hitap_ack ???
"""

class Employee(Model):

    first_name = field.String("Adı", index=True)
    last_name = field.String("Soyadı", index=True)
    staff_type = field.String("Personel Türü", index=True)
    birth_date = field.Date("Doğum Tarihi", index=True)
    mobile_phone = field.String("Cep Telefonu", index=True)
    pno = field.String("TC No", index=True)

    class ServiceRecords(ListNode):
        start_date = field.Date("Başlangıç Tarihi", index=True, format="%d.%m.%Y")
        end_date = field.Date("Bitiş Tarihi", index=True, format="%d.%m.%Y")
        retirement_degree = field.Integer("Emeklilik Derece", index=True)
        retirement_grade = field.Integer("Emeklilik Kademe", index=True)
        assignment = field.String("Görev", index_as='text_tr')
        title_code = field.Integer("Ünvan Kodu", index=True)
        duty_class = field.String("Hizmet Sınıfı", index=True)
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
        pno = field.String("TC No", index=True)
        salary = field.Float("Ücret", index=True)
        wage = field.Float("Yemiye", index=True)
        approval_date = field.Date("Kurum Onay Tarihi", index=True)

