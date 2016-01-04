# -*- coding: utf-8 -*-
from test_settings import Settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestCase(Settings):
    def test_dashboard(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Panel'e tikliyor.
        self.driver.find_element_by_css_selector('#side-menu > li:nth-child(1)').click()
        # Personel'e deger yolluyor
        self.driver.find_element_by_css_selector('.dashboard-personnel-search > div:nth-child(1) > input:nth-child(2)').send_keys('123')
        self.do_login()
        # Personel'e deger yolluyor
        self.driver.find_element_by_css_selector('.dashboard-personnel-search > div:nth-child(1) > input:nth-child(2)').send_keys('123')
        # Per7'i seciyor.
        self.driver.find_element_by_css_selector('ul.ng-scope > li:nth-child(1) > a:nth-child(1)').click()
        self.driver.find_element_by_css_selector('ul.ng-scope > li:nth-child(1) > a:nth-child(1)').click()
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'li.ng-binding:nth-child(1) > a:nth-child(1) > span:nth-child(2)')))

    def test_sidebar(self):
        # Secime Uygun Gorevleri seciyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(1) > a:nth-child(1) > span:nth-child(2)').click()
        # Kurum Ici Gorevlendirmeler'e tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(5) > a:nth-child(1)').click()
        # Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn').click()
        # Gorev Tipi seciyor.
        self.driver.find_element_by_css_selector('#gorev_tipi').click()
        self.driver.find_element_by_css_selector('#gorev_tipi > option:nth-child(3)').click()
        # Baslama Tarihi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#kurum_ici_gorev_baslama_tarihi').send_keys('12.04.2000')
        # Bitis Tarihine deger yolluyor.
        self.driver.find_element_by_css_selector('#kurum_ici_gorev_bitis_tarihi').send_keys('12.05.2002')
        # Aciklama'ya deger yolluyor.
        self.driver.find_element_by_css_selector('#aciklama').send_keys('aciklama')
        # Resmi Yazi Sayi'ya deger yolluyor.
        self.driver.find_element_by_css_selector('#resmi_yazi_sayi').send_keys('resmi')
        # Unit seciyor.
        self.driver.find_element_by_css_selector('button.dropdown-toggle').click()
        # Birimlerin yuklenmesini bekliyor.
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)')))
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').click()
        # Kaydet ve Listele'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()









