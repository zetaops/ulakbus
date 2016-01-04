# -*- coding: utf-8 -*-
from test_settings import Settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class TestCase(Settings):

    def test_sidebar(self):
        # Panel tusunu gorene kadar test_user login olmasini on saniye bekliyor.
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#side-menu > li:nth-child(1) > a:nth-child(1)')))
        # Personal alanina '123' yaziyor.
        self.driver.find_element_by_css_selector(
            '.dashboard-personnel-search > center:nth-child(1) > input:nth-child(2)').send_keys('123')
        # Per7'i seciyor.
        self.driver.find_element_by_css_selector('ul.ng-scope:nth-child(1) > li:nth-child(1) > a:nth-child(1)').click()
        # Secime Uygun Gorevler'e tikliyor
        self.driver.find_element_by_css_selector(
            'li.ng-binding:nth-child(2) > a:nth-child(1) > span:nth-child(2)').click()
        # Kurum Disi Gorevlendirmeleri tusunu bulana kadar on saniye bekliyor.
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)')))
        # Kurum Disi Gorevlendirmeler'i  buluyor.
        content = self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(2) > a:nth-child(1)')
        assert content.text == 'Kurum Disi Gorevlendirmeler'
        content.click()
        # Ekle  tusuna tikliyor
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn-danger')))
        self.driver.find_element_by_css_selector('.btn-danger').click()
        # Gorev Tipi'ni bulana kadar on saniye bekliyor.
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#gorev_tipi')))
        # Gorev Tipi'ne deger yolluyor.
        self.driver.find_element_by_css_selector('#gorev_tipi').send_keys('54')
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#kurum_disi_gorev_baslama_tarihi')))
        # Baslama Tarihi'ni seciyor ve deger yolluyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(3) > div:nth-child(1) > p:nth-child(2) > span:nth-child(1) > button:nth-child(1)').click()
        lst = self.driver.find_elements_by_css_selector('ul.ng-valid-date-disabled td')
        # 16'a tikliyor.
        lst[20].click()
        # Bitis Tarihi'ni seciyor ve deger yolluyor.
        self.driver.find_element_by_css_selector('#kurum_disi_gorev_bitis_tarihi').click()
        lst = self.driver.find_elements_by_css_selector('ul.ng-valid-date-disabled td')
        # 16'a tikliyor.
        lst[20].click()
        self.driver.find_element_by_css_selector('#aciklama').send_keys('aciklama')
        self.driver.find_element_by_css_selector('#resmi_yazi_sayi').send_keys('1')
        self.driver.find_element_by_css_selector('#resmi_yazi_tarih').clear()
        self.driver.find_element_by_css_selector('#resmi_yazi_tarih').send_keys('12.04.1995')
        # Yevmiye'ye tikliyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(9) > div:nth-child(1) > label:nth-child(1) > span:nth-child(2)').click()
        # ulke alanina tikliyor
        self.driver.find_element_by_css_selector('#ulke').click()
        # Hollanda'yi seciyor.
        self.driver.find_element_by_css_selector('#ulke > option:nth-child(4)').click()
        # Kaydet ve Listele tusuna basiyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()
        # Belcika'yi seciyor.
        self.driver.find_element_by_css_selector('div.in > div:nth-child(1) > label:nth-child(1)').click()
        # Gorev Tipi'ne tikliyor.
        self.driver.find_element_by_css_selector(
            '.col-md-4 > div:nth-child(4) > div:nth-child(1) > div:nth-child(1) > h5:nth-child(1)').click()
        # Ilk degeri(54) seciyor.
        self.driver.find_element_by_css_selector(
            '.col-md-4 > div:nth-child(4) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > label:nth-child(1) > input:nth-child(1)').click()
        # Baslama Tarihi'ne tikliyor.
        self.driver.find_element_by_css_selector(
            '.col-md-4 > div:nth-child(5) > div:nth-child(1) > div:nth-child(1) > h5:nth-child(1)').click()
        # Baslagic'a deger yolluyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(1) > p:nth-child(2) > input:nth-child(2)').send_keys('16.12.2015')
        # Bitis'e deger yolluyor.
        self.driver.find_element_by_css_selector(
            'div.col-md-12:nth-child(2) > p:nth-child(2) > input:nth-child(2)').send_keys('16.12.2015')
        # Filtrele tusuna tikliyor.
        self.driver.find_element_by_css_selector('.btn-warning').click()
        # On saniye uyutuyor.
        time.sleep(10)
        lst = self.driver.find_elements_by_css_selector('tr.ng-scope')
        # Filtrelemenin dogru yapilip yapilmadigini kontrol ediyor.
        for element in lst:
            sub_lst = element.text.split(' ')
            print sub_lst
            assert sub_lst[1] == 'Belçika'.decode('utf-8')
            assert sub_lst[2].encode('utf-8') == 54
            assert sub_lst[3] == '16.12.2015'
        


        # vdisplay.stop()
