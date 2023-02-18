from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from time import sleep, strftime
from random import randint
from bs4 import BeautifulSoup
import json

import simple_request

browser = webdriver.Firefox(firefox_binary = '/opt/firefox-dev/firefox')
sleep(2)
browser.get('https://www.instagram.com/explore/tags/%D8%A8%D8%A7%D8%B2%DB%8C%DA%AF%D8%B1%D8%A7%D9%86_%D8%B2%D9%86/')
sleep(7)
feed = browser.find_element_by_xpath('/html/body/span/section/main/article/div[1]/div/div/div[1]/div[1]/a/div/div[2]')
feed.click()

for i in range(10):
    sleep(3)
    try:
        next_btn = browser.find_element_by_xpath('/html/body/div[3]/div[1]/div/div/a[2]')
        next_btn.click()
    except NoSuchElementException:
        next_btn = browser.find_element_by_xpath('/html/body/div[3]/div[1]/div/div/a')
        next_btn.click()
close_btn = browser.find_element_by_xpath('/html/body/div[3]/button[1]')
close_btn.click()