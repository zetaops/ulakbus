# -*- coding: utf-8 -*-
from test_settings import Settings


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector(
            'li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Ogrenci Iletisim Bilgilerine tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        self.do_login()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector(
            'li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Ogrenci Iletisim Bilgilerine tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Ikamet Il'e deger gonderiyor.
        self.driver.find_element_by_css_selector('#ikamet_il').send_keys('Bilecik')
        # Ikamet Ilce'ye deger gonderiyor.
        self.driver.find_element_by_css_selector('#ikamet_ilce').send_keys('Merkez')
        # Ikametgah Adresine deger yolluyor.
        self.driver.find_element_by_css_selector('#ikamet_adresi').send_keys('balim sokak')
        # Posta Kodu'na deger yolluyor.
        self.driver.find_element_by_css_selector('#posta_kodu').send_keys('11000')
        # Telefon Numarasi'na deger yolluyor.
        self.driver.find_element_by_css_selector('#tel_no').send_keys('0534626286816')
        # Kaydet'e tikliyor
        self.driver.find_element_by_css_selector('button.btn-danger:nth-child(1)').click()
