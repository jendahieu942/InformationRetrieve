import time

import pymongo.errors
import scrapy
import hashlib
from pymongo import MongoClient
from scrapy import Selector
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class RestaurantSpider(scrapy.Spider):
    name = "restaurants"
    start_urls = ["https://www.foody.vn/ha-noi"]

    def __init__(self):
        # self.driver = webdriver.Chrome('/usr/local/share/chromedriver/chromedriver')
        self.main_window = webdriver.Chrome('/usr/local/share/chromedriver/chromedriver')
        self.rest_window = webdriver.Chrome('/usr/local/share/chromedriver/chromedriver')
        self.mongoUtils = MongoUtils('hieutv', 'info_retrieve')

    def parse(self, response):
        self.main_window.get(response.url)

        # collect only do_an, do_uong, trang_mieng, ...
        for index_type in range(1, 8):
            type_button = self.main_window.find_element_by_css_selector(
                '#box-delivery > div.n-header > div.nav-box > ul > li:nth-child(%s)' % str(index_type))
            type_button.click()
            # Wait until page loaded
            for count_side in range(50):
                try:
                    element_present = EC.presence_of_all_elements_located(
                        (By.XPATH, '//*[@id="box-delivery"]/div[2]/ul/li[10]/div[1]/a[1]/img'))
                    WebDriverWait(self.main_window, 30).until(element_present)
                    self.getRestaurant(self.main_window.page_source)
                except TimeoutException:
                    print("Time out while wait page loaded")
                # next to other side
                try:
                    next_side = self.main_window.find_element_by_css_selector(
                        '#box-delivery > div.n-listitems > i.li-page.fa.fa-angle-right.ng-scope.ng-enter-prepare')
                    next_side.click()
                except (NoSuchElementException, WebDriverException) as e:
                    print("No side more")
                    print(e)
                    pass
        self.main_window.close()
        self.rest_window.close()

    def parseMenu(self):
        menu = {}
        last_scroll_height = self.rest_window.execute_script("return document.body.scrollHeight")
        offset_scroll = 0
        while True:
            res = Selector(text=self.rest_window.page_source)
            time.sleep(1.5)
            menu_div = res.xpath('//*[@id="restaurant-item"]/div/div')
            menu_list = menu_div.css('.item-restaurant-row')
            for meal in menu_list:
                name = meal.css('.item-restaurant-name::text').get()
                img_meal = meal.css('.inline img::attr(src)').get()
                desc = meal.css('.item-restaurant-desc::text').get()
                desc = desc if desc is not None else 'empty'
                price = meal.css('.current-price::text').get().replace(',', '')
                item = {'name': name, 'price': price, 'desc': desc, 'img': img_meal}

                if name not in menu.keys():
                    menu[name] = item

            # Scroll down
            self.rest_window.execute_script("window.scrollBy(0, 2000);")
            if offset_scroll >= last_scroll_height:
                new_scroll_height = self.rest_window.execute_script("return document.body.scrollHeight")
                if new_scroll_height == last_scroll_height:
                    break
                last_scroll_height = new_scroll_height
            offset_scroll += 2000

        return menu

    def getRestaurant(self, body):
        res = Selector(text=body)
        for info in res.xpath('//*[@id="box-delivery"]/div[2]/ul/li'):
            res_detail = {}

            # parse info
            link = info.css('a.avatar::attr(href)').get()
            avatar = info.css('a.avatar img::attr(src)').get()
            name = info.css('span.none-quality-text.ng-binding ::text').get()
            address = info.css('div.address.limit-text.ng-binding ::text').get().replace(',', ' -')
            salt = name + address
            key = hashlib.sha256(salt.encode()).hexdigest()
            print(key)
            if self.mongoUtils.isExisted(key):
                print("Continue")
                continue

            # parse menu
            self.rest_window.get(link)
            try:
                element_present = EC.presence_of_all_elements_located((By.XPATH, '//*[@id="scroll-spy"]/div/div[1]'))
                WebDriverWait(self.rest_window, 30).until(element_present)
            except TimeoutException:
                print("Time out while wait menu load")
                continue
            tag = Selector(text=self.rest_window.page_source) \
                .css('.kind-restaurant::text') \
                .get()
            menu = self.parseMenu()

            # add to dict
            res_detail['_id'] = key
            res_detail['name'] = name
            res_detail['link'] = link
            res_detail['avatar'] = avatar
            res_detail['address'] = address
            res_detail['tag'] = tag
            res_detail['menu'] = [meal for meal in sorted(menu.values(), key=lambda x: x['name'])]
            self.mongoUtils.insert_one(res_detail)


class MongoUtils:
    def __init__(self, database_name, collection_name):
        self.client = MongoClient('mongodb://localhost:27017')
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def showDatabases(self):
        print(self.client.list_database_names())

    def showCollections(self):
        print(self.database.list_collection_names())

    def isExistedDB(self, db_name):
        db_list = self.client.list_database_names()
        if db_name in db_list:
            return True
        return False

    def insert_one(self, doc):
        try:
            self.collection.insert_one(doc)
        except pymongo.errors.DuplicateKeyError:
            print('ERROR: Key is already existed. This document will be update')
            self.collection.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)

    def insert_many(self, list):
        self.collection.insert_many(list)

    def isExisted(self, id):
        items = self.collection.find({'_id': id})
        return True if items.count() > 0 else False
