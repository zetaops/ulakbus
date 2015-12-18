# -*- coding: utf-8 -*-
from test_settings import Settings


class TestCase(Settings):
    def test_yetki(self):
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

    def test_bina(self):
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Bina'ya tikliyor.
        self.driver.find_element_by_css_selector('li.ng-scope:nth-child(14) > a:nth-child(1)').click()
        # Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn').click()
        # Code'ye deger yolluyor.
        self.driver.find_element_by_css_selector('#code').send_keys('A9')
        # Name deger yolluyor.
        self.driver.find_element_by_css_selector('#name').send_keys('Amfi')
        # Coordinate X'e deger yolluyor.
        self.driver.find_element_by_css_selector('#coordinate_x').send_keys('x')
        # Coordinate Y'ye deger yolluyor.
        self.driver.find_element_by_css_selector('#coordinate_y').send_keys('y')
        # Permission Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('.fa-plus-circle').click()
        # Code'ye deger yolluyor
        self.driver.find_element_by_css_selector(
            'form.ng-pristine:nth-child(4) > bootstrap-decorator:nth-child(2) > div:nth-child(1) > input:nth-child(2)').send_keys('kod')
        # Name deger yolluyor.
        self.driver.find_element_by_css_selector(
            'form.ng-pristine:nth-child(4) > bootstrap-decorator:nth-child(3) > div:nth-child(1) > input:nth-child(2)').send_keys('iyte')
        # Coordinate X'e deger yolluyor.
        self.driver.find_element_by_css_selector('form.ng-pristine:nth-child(4) > bootstrap-decorator:nth-child(4) > div:nth-child(1) > input:nth-child(2)').send_keys('X')
        # Coordinate Y'e deger yolluyor.
        self.driver.find_element_by_css_selector('form.ng-pristine:nth-child(4) > bootstrap-decorator:nth-child(5) > div:nth-child(1) > input:nth-child(2)').send_keys('Y')
        # Kaydet'e Tikliyor.
        self.driver.find_element_by_css_selector('button.move-to-bottom-modal:nth-child(1)').click()
        # Kaydet ve Listele'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)').click()

    def test_oda(self):
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Oda'ya tikliyor.
        self.driver.find_element_by_css_selector('li.ng-scope:nth-child(15) > a:nth-child(1)').click()
        # Code deger yoluyor.
        self.driver.find_element_by_css_selector('#code').send_keys('20')
        # Name deger yolluyor.
        self.driver.find_element_by_css_selector('#name').send_keys('oda')
        # Floor'a deger yolluyor.
        self.driver.find_element_by_css_selector('#floor').send_keys('1')
        # Capasite'ye deger yolluyor.
        self.driver.find_element_by_css_selector('#capacity').send_keys('25')
        # Bina'ya tikliyor.
        self.driver.find_element_by_css_selector('.open > button:nth-child(1)').click()
        # Binalarin yuklenmesini bekliyor.
        WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)')))
        # Bina seciyor.
        self.driver.find_element_by_css_selector('.open > ul:nth-child(2) > li:nth-child(1) > a:nth-child(1)').click()
        # Room Type ekliyor.
        self.driver.find_element_by_css_selector(
            'bootstrap-decorator.ng-scope:nth-child(12) > div:nth-child(1) > div:nth-child(1) > a:nth-child(2) > i:nth-child(1)').click()
        self.driver.find_element_by_css_selector('#type').send_keys('type')
        # Notes ekliyor.
        self.driver.find_element_by_css_selector('#notes').send_keys('aciklama')
        # Kaydet'e tikliyor.
        self.driver.find_element_by_css_selector('button.move-to-bottom-modal:nth-child(1)').click()
        # Kaydet ve Listele'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(2)')

    def test_kampus(self):
        # Admin'e tikliyor.
        self.driver.find_element_by_css_selector('li.ng-binding:nth-child(4) > a:nth-child(1)').click()
        # Kampus'e tikliyor
        self.driver.find_element_by_css_selector('li.ng-scope:nth-child(13) > a:nth-child(1)').click()
        # Ekle'ye tikliyor.
        self.driver.find_element_by_css_selector('.btn-danger').click()
        # Code deger yolluyor.
        self.driver.find_element_by_css_selector('#code').send_keys('kamp')
        # Name deger yolluyor.
        self.driver.find_element_by_css_selector('#name').send_keys('dokuz eylul')
        # Coordinate X'e deger yolluyor.
        self.driver.find_element_by_css_selector('#coordinate_x').send_keys('x')
        # Coordinate Y'ye deger yolluyor.
        self.driver.find_element_by_css_selector('#coordinate_y').send_keys('y')
        # Kaydet ve Listele'ye tikliyor.
        self.driver.find_element_by_css_selector('button.btn:nth-child(1)').click()







