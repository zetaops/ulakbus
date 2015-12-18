# -*- coding: utf-8 -*-
from test_settings import Settings


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Yetki'ye tikliyor
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(3) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.do_login()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Yetki'ye tikliyor
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(3) > a:nth-child(1)').click()
        # Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('.btn-danger').click()
        # Isim'e deger yolluyor,
        self.driver.find_element_by_css_selector('#name').send_keys('memnur')
        # Kod Adi'na deger yolluyor.
        self.driver.find_element_by_css_selector('#code').send_keys('code')
        # Tanim'a deger yolluyor.
        self.driver.find_element_by_css_selector('#description').send_keys('tanim')
        # Kaydet ve Listele'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()