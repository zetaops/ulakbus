# -*- coding: utf-8 -*-
from selenium import webdriver
from page_objects import PageObject, PageElement


class LoginPage(PageObject):
    username = PageElement(id_='username')
    password = PageElement(id_='password')
    login = PageElement(css='input[type="submit"]')
    form = PageElement(tag_name='form')
    driver = webdriver.Firefox()

    def __init__(self):
        super(LoginPage, self).__init__(self.driver, root_uri="http://nightly.ulakbus.net/#/login")

    def do_login(self):
        self.get('')
        self.username = 'test_user'
        self.password = '123'
        self.login.click()
LoginPage().do_login()
