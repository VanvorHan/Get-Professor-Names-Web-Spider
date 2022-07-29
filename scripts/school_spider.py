import re
import csv
import requests
import pandas as pd

from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class School():
    def __init__(self, name, ID, ABBR, URL):
        self.name = name
        self.ID = ID
        self.ABBR = ABBR
        self.URL = URL
        self.depart_list = []


class Spider():
    def __init__(self):
        chrome_ADDR = '/Users/vanvorhan/Desktop/SchoolSpider/chromedriver'

        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium

        self.driver = webdriver.Chrome(executable_path=chrome_ADDR, options=options)
        self.wait = WebDriverWait(self.driver, 10)  # 超时时长为10s

        self.db_URL = "http://xuankebao-bms.uuudoo.com/index.php?s=/Department/index.html"
        sleep_time = 1.5

    def get_departs(self, school):
        self.driver.get(school.URL)

        self.driver.implicitly_wait(30)  # 智能等待，直到网页加载完毕，最长等待时间为30s
        self.driver.find_element_by_xpath('/html/body/nav/div/div/div/ul/li[2]/a').click()

        depart_web_list = self.driver.find_element_by_xpath('//*[@id="wp_content_w89_0"]/div/div[3]/div/ul')
        items = depart_web_list.find_elements_by_tag_name("a")
        for item in items:
            if not item.text or item.text == "金陵学院" or item.text == "新生学院":
                continue
            link = item.get_attribute("href")
            school.depart_list.append({'depart': item.text, 'link': link, 'id': None})

    '''
        #items = depart_web_list.find_elements_by_tag_name("li")
        #for item in items:
            #print(item.get_attribute("href"))
         #   text = item.text
            #link = item.get_attribute("href")
         #   school.depart_list.append(text)
    def input_departs(self, school):
        self.driver.get(self.db_URL)
        self.driver.implicitly_wait(30) #智能等待，直到网页加载完毕，最长等待时间为30s
    '''


def get_professor(user_name, school_name, depart_name, link):
    row_list = []
    '''
    target_attr = {'class': 'cols_title'}
    r = requests.get(link)
    # self.driver.get(link)
    # page_source = self.driver.page_source

    # row_list = [["用户昵称", "学校名称", "教授名称", "院系名称"]]
    print(r.text)
    soup = BeautifulSoup(r.text, "html.parser")
    al = soup.find_all(attrs=target_attr)
    for a in al:
        p_name = re.sub(r"\s+", "", a.text, flags=re.UNICODE)
        row = [user_name, school_name, p_name ,depart_name]
        row_list.append(row)
    '''
    '''
    t_list = self.driver.find_element_by_xpath('//*[@id="ajaxpage-list"]')
    items = t_list.find_elements_by_tag_name("a")
    for item in items:
        p_name = re.sub(r"\s+", "", item.text, flags=re.UNICODE)
        row = ["admin", "南京大学", p_name, "文学院"]
        row_list.append(row)

    self.driver.find_element_by_xpath("//*[@id='pages']/a[2]").click()


    t_list = self.driver.find_element_by_xpath('//*[@id="ajaxpage-list"]')
    items = t_list.find_elements_by_tag_name("a")
    for item in items:
        p_name = re.sub(r"\s+", "", item.text, flags=re.UNICODE)
        row = ["admin", "南京大学", p_name, "文学院"]
        row_list.append(row)
    '''
    print(row_list)
    exit()
    with open('professor.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)

    read_file = pd.read_csv(r'professor.csv')
    read_file.to_excel(r'professor.xls', index=None, header=True)

# school = School("南京大学", 7, "NJU", "https://www.nju.edu.cn/main.htm")
#spider = Spider()
# spider.get_departs(school)
# print(school.depart_list)
# spider.input_departs(school)
# spider.get_professor(school)
# spider.get_professor("文学院", 1, "https://chin.nju.edu.cn//szdw/xrjs/index.html")
get_professor("Zero", "南京大学", "历史学院（NYU）", "https://history.nju.edu.cn/28475/list.htm")
# spider.driver.close()
