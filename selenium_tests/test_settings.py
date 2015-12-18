# -*- coding: utf-8 -*-

from test_login import Logging


class Settings(Logging):
    def do_settings(self):
        # Kullaniciya giris yaptiriyor.
        self.do_login()
        self.driver.find_element_by_css_selector('li.dropdown:nth-child(4) > a:nth-child(1)').click()
        # Ayarlar(dev)'e tikliyor.
        self.driver.find_element_by_css_selector('.dropdown-menu > li:nth-child(4) > a:nth-child(1)').click()
        # Backend Url'ye deger gonderiyor.
        self.driver.find_element_by_css_selector('.form-control').send_keys('https://test.ulakbus.net/')
        # Kaydet'e tikliyor
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()

