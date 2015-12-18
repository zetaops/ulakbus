from test_settings import Settings


class TestCase(Settings):
    def test_sidebar(self):
        # Ayarlari yapiyor.
        self.do_settings()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector(
            'li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Onceki Egitim Bilgilerine tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(6) > a:nth-child(1)').click()
        # Backend ayarlari degistirildigi icin tekrar kullanicinin login olmasini bekliyor.
        self.do_login()
        # Genel'e tikliyor.
        self.driver.find_element_by_css_selector(
            'li.ng-binding:nth-child(3) > a:nth-child(1) > span:nth-child(2)').click()
        # Onceki Egitim Bilgilerine tikliyor.
        self.driver.find_element_by_css_selector('ul.in:nth-child(2) > li:nth-child(6) > a:nth-child(1)').click()
        # Mezun Oldugu Okula deger yolluyor.
        self.driver.find_element_by_css_selector('#okul_adi').send_keys('Anadolu Lisesi')
        # Diploma Notu'na deger yolluycam.
        self.driver.find_element_by_css_selector('#diploma_notu').send_keys('76')
        # Mezuniyet Yili'na deger yolluyor.
        self.driver.find_element_by_css_selector('#mezuniyet_yili').send_keys('2008')
        # Kaydet'e tikliyor.
        self.driver.find_element_by_css_selector('.btn-danger').click()

