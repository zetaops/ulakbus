# -*- coding: utf-8 -*-
from test_settings import Settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Rol'e tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.do_login()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Rol'e tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()

    def test_roller(self):
        # Ilk satirin duzenle tusuna tikliyor.
        self.driver.find_element_by_css_selector(
            'tr.ng-scope:nth-child(1) > td:nth-child(4) > button:nth-child(1)').click()
        # Unit'e tikliyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(6) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1) > button:nth-child(1)').click()
        # Birimlerin yuklenmesini bekliyor.
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)')))
        # Temel Yabanci Diller Bolumu'nu seciyor.
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Kullanici'ya tikliyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(7) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1)').click()
        # User tarik'i seciyor
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(4) > a:nth-child(1)').click()
        # Soyut Rol'e tikliyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(8) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1) > button:nth-child(1)').click()
        # User fakir'i seciyor.
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(6) > a:nth-child(1)').click()
        # Permission ekle'ye tikliyor
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(9) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > i:nth-child(1)').click()
        # Hata mesaji aliyorsa hatayi ekrana basiyor ve hata mesajini kapatiyor.
        self.driver.find_element_by_css_selector('.modal-footer > button:nth-child(1)').click()
        # Permissions List'e seciyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(2) > select:nth-child(2) > option:nth-child(1)').click()
        # Secilenlerden deger seciyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(4) > select:nth-child(2) > option:nth-child(1)').click()
        # Kaydet'e tikliyor.
        self.driver.find_element_by_css_selector('button.btn-danger:nth-child(1)').click()

