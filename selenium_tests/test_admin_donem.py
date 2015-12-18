# -*- coding: utf-8 -*-
from test_settings import Settings


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Donem'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-scope:nth-child(9) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.do_login()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Donem'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-scope:nth-child(9) > a:nth-child(1)').click()
        # Donem'e deger yolluyor.
        self.driver.find_element_by_css_selector('#ad').send_keys('Guz Donemi')
        # Baslangic Tarihi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#baslangic_tarihi').send_keys('13.04.2009')
        # Bitis Tarihi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#bitis_tarihi').send_keys('11.06.2013')
        # guncel'e tikliyor.
        self.driver.find_element_by_css_selector('.checkbox > label:nth-child(1) > input:nth-child(1)').click()
        # Kaydet ve Listeleye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()
