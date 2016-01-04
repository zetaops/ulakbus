# -*- coding: utf-8 -*-
from test_settings import Settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Ders Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(5) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.do_login()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Ders Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(5) > a:nth-child(1)').click()

    def test_ders(self):
        # Program seciyor.
        self.driver.find_element_by_css_selector('button.dropdown-toggle').click()
        # Programlarin yuklenmesini bekliyor.
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.input-group-btn > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)')))
        self.driver.find_element_by_css_selector('.input-group-btn > ul:nth-child(2) > li:nth-child(3) > a:nth-child(1)').click()
        # Sec'e tikliyor.
        self.driver.find_element_by_css_selector('.btn-danger').click()
        # Ad'a deger gonderiyor.
        self.driver.find_element_by_css_selector('#ad').send_keys('Matematik')
        # Kod'a deger gonderiyor.
        self.driver.find_element_by_css_selector('#kod').send_keys('413')
        # Tanim'a deger yolluyor.
        self.driver.find_element_by_css_selector('#tanim').send_keys('tanim')
        # Aciklama'ya deger yolluyor.
        self.driver.find_element_by_css_selector('#aciklama').send_keys('aciklama')
        # On Kosul'a deger yolluyor.
        self.driver.find_element_by_css_selector('#onkosul').send_keys('On kosul')
        # Uygulama Testi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#uygulama_saati').send_keys('10.00')
        # Teori Saati'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#teori_saati').send_keys('9.00')
        # ECTS Kredisi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#ects_kredisi').send_keys('3')
        # Yerel Kredisi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#yerel_kredisi').send_keys('4')
        # Ders Dili'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#ders_dili').send_keys('Ingilicce')
        # Ders Turu'ne tikliyor.
        self.driver.find_element_by_css_selector('#ders_turu').click()
        # Ders Turu seciyor.
        self.driver.find_element_by_css_selector('#ders_turu > option:nth-child(3)').click()
        # Ders Amaci'na deger yolluyor.
        self.driver.find_element_by_css_selector('#ders_amaci').send_keys('amacsiz')
        # Ogrenme Ciktilarina deger yolluyor.
        self.driver.find_element_by_css_selector('#ogrenme_ciktilari').send_keys('ogrenme')
        # Ders Icerigine deger yolluyor.
        self.driver.find_element_by_css_selector('#ders_icerigi').send_keys('Icerik')
        # Ders Kategorisi'ne tikliyor.
        self.driver.find_element_by_css_selector('#ders_kategorisi').click()
        # Ders Kategorisi seciyor.
        self.driver.find_element_by_css_selector('#ders_kategorisi > option:nth-child(3)').click()
        # Ders Kaynaklari'na deger yolluyor.
        self.driver.find_element_by_css_selector('#ders_kaynaklari').send_keys('kaynak')
        # Ders Mufredati'na deger yolluyor.
        self.driver.find_element_by_css_selector('#ders_mufredati').send_keys('mufredat')
        # Verilis Bicimi'ne tikliyor.
        self.driver.find_element_by_css_selector('#verilis_bicimi').click()
        # Verilis bicimi seciyor.
        self.driver.find_element_by_css_selector('#verilis_bicimi > option:nth-child(2)').click()
        # Personel seciyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(23) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > span:nth-child(1) > button:nth-child(1)').click()
        # Personellerin yuklenmesini bekliyor.
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)')))
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(2) > a:nth-child(1)').click()
        # Donem seciyor.
        self.driver.find_element_by_css_selector('.open > button:nth-child(1)').click()
        # Donemlerin yuklenemesini bekliyor.
        WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)')))
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').click()
        # Kaydet'e tikliyor.
        self.driver.find_element_by_css_selector('button.btn-danger:nth-child(1)').click()
        # !!!!!!!!!!! Formu iki kere dolduruyor.






