# -*- coding: utf-8 -*-
try:
    from selenium import webdriver
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
except:
    print("Selenium cannot be imported")


class BaseTestCase(object):
    driver = None

    @classmethod
    def make_driver(cls):
        cls.driver = webdriver.Firefox()
        cls.driver.get('http://nightly.ulakbus.net/#/dashboard')
        cls.driver.implicitly_wait(10)

    def do_login(self):
        self.make_driver()
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


BaseTestCase.make_driver()
