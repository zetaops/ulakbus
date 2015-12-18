# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Logging(object):
    driver = webdriver.Firefox()
    driver.get('http://nightly.ulakbus.net/#/dashboard')
    driver.implicitly_wait(10)

    def do_login(self):
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
