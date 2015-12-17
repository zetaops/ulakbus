# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestCase():
    driver = webdriver.Firefox()
    # Anasayfa'ya gidiyor.
    driver.get('http://nightly.ulakbus.net/#/dashboard')
    driver.implicitly_wait(10)

    def test_login(self):
        email_field = self.driver.find_element_by_id("username")
        # Kullanici adi alanina 'test_user' yolluyor.
        email_field.send_keys("test_user")
        password_field = self.driver.find_element_by_id("password")
        # Sifre alanina '123' yolluyor.
        password_field.send_keys("123")
        # Giris tusuna tikliyor.
        self.driver.find_element_by_css_selector('.btn').click()
        # Panel tusunu gorene kadar test_user login olmasini 25 saniye bekliyor.
        WebDriverWait(self.driver, 25).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#side-menu > li:nth-child(1) > a:nth-child(1)')))

    def test_settings(self):
        self.driver.find_element_by_css_selector('li.dropdown:nth-child(4) > a:nth-child(1)').click()
        # Ayarlar(dev)'e tikliyor.
        self.driver.find_element_by_css_selector('.dropdown-menu > li:nth-child(4) > a:nth-child(1)').click()
        # Backend Url'ye deger gonderiyor.
        self.driver.find_element_by_css_selector('.form-control').send_keys('https://test.ulakbus.net/')
        # Kaydet'e tikliyor
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()

    def test_sidebar(self):
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Rol'e tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.test_login()
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Rol'e tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Ilk satirin duzenle tusuna tikliyor.
        self.driver.find_element_by_css_selector(
            'tr.ng-scope:nth-child(1) > td:nth-child(4) > button:nth-child(1)').click()
        # Soyut Rol seciyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(6) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1)').click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)')))
        # test rol'u seciyor.
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').click()
        # Kullanici seciyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(7) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1)').click()
        # User servet'i seciyor
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(5) > a:nth-child(1)').click()
        # Unit seciyor
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(8) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1)').click()
        # Birimlerin yuklenmesi bekliyor
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)')))
        # Modern Diller Bolumu'nu seciyor.
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)').click()
        # Permission ekle'ye tikliyor
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(9) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > i:nth-child(1)').click()
        # Hata mesaji aliyorsa hatayi ekrana basiyor ve hata mesajini kapatiyor.
        if self.driver.find_element_by_css_selector('pre').is_displayed():
            print self.get_error_message()
            self.driver.find_element_by_css_selector(
                '.modal-footer > button:nth-child(1)').click()
        # Permissions List'e seciyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(2) > select:nth-child(2) > option:nth-child(1)').click()
        # Secilenlerden deger seciyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(4) > select:nth-child(2) > option:nth-child(1)').click()
        #  Kaydet ve listeleye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()

    def get_error_message(self):
        message_box = self.driver.find_element_by_css_selector('pre')
        return message_box.text
