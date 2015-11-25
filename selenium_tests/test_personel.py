# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime

class TestCase():
    driver = webdriver.Firefox()

    def test_login(self):
        # ulakbus homepage gidiyor.
        # self.driver.get('http://nightly.ulakbus.net/#/dashboard')
        self.driver.get('http://ulakbus-remote-dev.zetaops.io:18180/?backendurl=http://ulakbus-remote-dev.zetaops.io:18188/')
        # Driver'i on saniye bekletiyor.
        self.driver.implicitly_wait(10)
        email_field = self.driver.find_element_by_id("username")
        #Kullanici adi kismina test_user yollaniyor
        email_field.send_keys("test_user")
        password_field = self.driver.find_element_by_id("password")
        # Sifre kismina 123 yollaniyor.
        password_field.send_keys("123")
        # Giris butonuna tikliyor.
        self.driver.find_element_by_css_selector('.btn').click()

    def test_dashboard(self):
        # Test user'in login olmasini bekliyor.
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/ul/li[2]/a')))
        # Personel placeholder'a kullanici sifresini yolluyor.
        # later = datetime.datetime.now()
        # print later
        self.driver.find_element_by_css_selector('.dashboard-personnel-search > center:nth-child(1) > input:nth-child(2)').send_keys('123')
        # Per8'i seciyor.
        self.driver.find_element_by_css_selector(
            'ul.ng-scope:nth-child(1) > li:nth-child(1) > a:nth-child(1)').click()
        # Genel butonuna tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(2) > a:nth-child(1) > span:nth-child(2)').click()
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/ul/li[2]/ul/li[5]/a')))
        foundation_field = self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)')
        assert foundation_field.text == 'Kurum İçi Görevlendirmeler'
        foundation_field.click()
        # Ekle butonuna tikliyor.
        self.driver.find_element_by_css_selector('.move-to-bottom').click()
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'gorev_tipi')))
        # Gorev tipine tikliyor
        self.driver.find_element_by_id('gorev_tipi').click()
        # Kurum ici gorev elementini buluyor.
        gorev_tipi_element = self.driver.find_element_by_css_selector('#gorev_tipi > option:nth-child(3)')
        gorev_tipi_element.click()
        assert gorev_tipi_element.text == 'kurum içi görev'
        self.driver.find_element_by_id('kurum_ici_gorev_baslama_tarihi').click()
        self.driver.find_element_by_css_selector('select.ui-datepicker-month > option:nth-child(9)').click()
        self.driver.find_element_by_css_selector('select.ui-datepicker-year > option:nth-child(12)').click()
        self.driver.find_element_by_css_selector('.ui-datepicker-calendar > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2) > a:nth-child(1)').click()
        # Baslama tarihine girilen tarihin degerini aliyor
        date_value = self.driver.find_element_by_id('kurum_ici_gorev_baslama_tarihi').get_attribute('value')
        assert date_value == '12.09.2016'

