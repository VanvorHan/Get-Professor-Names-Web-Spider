import re
import time
import requests

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

chrome_ADDR = '/Users/vanvorhan/Desktop/SchoolSpider/chromedriver'


class DataInputer:
    db_link = "http://xuankebao-bms.uuudoo.com/index.php?s=/Login/login.html"

    def __init__(self):
        options = webdriver.ChromeOptions()
        # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # 不加载图片,加快访问速度
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
        self.driver = webdriver.Chrome(executable_path=chrome_ADDR, options=options)

    def db_login(self):
        driver = self.driver

        driver.get(self.db_link)
        driver.implicitly_wait(30)  # 智能等待，直到网页加载完毕，最长等待时间为30s

        driver.find_element_by_xpath('//*[@id="loginform"]/div[1]/div/div/input').send_keys("admin")
        driver.find_element_by_xpath('//*[@id="loginform"]/div[2]/div/div/input').send_keys("123456")

        time.sleep(10)
        driver.find_element_by_xpath('//*[@id="loginform"]/div[6]/span[2]/button').click()
        # login in button
        time.sleep(20)

        driver.find_element_by_xpath('//*[@id="sidebar"]/ul/li[6]/a/span[1]').click()
        # 院系管理 button
        driver.find_element_by_xpath('//*[@id="sidebar"]/ul/li[6]/ul/li/a').click()
        # 院系列表 button
        # dept_list = ['建筑学院', '机械工程学院']

        time.sleep(2)

    def each_input_db(self, dept_list, uni_name, uni_abbr):
        driver = self.driver
        for dept in dept_list:
            driver.find_element_by_xpath('//*[@id="content"]/div[4]/div[1]/div/div/div[1]/button[1]').click()
            # 新增 button

            dept_name = dept + '（' + uni_abbr + '）'
            driver.find_element_by_xpath(
                '//*[@id="content"]/div[4]/div[1]/div/div/div/form/div[1]/div/input').send_keys(
                dept_name)
            driver.find_element_by_xpath(
                '//*[@id="content"]/div[4]/div[1]/div/div/div/form/div[2]/div/div/button[2]').click()
            # school selection drop down button

            tmp_css_selector = 'li[data-title="' + uni_name + '"]'
            driver.find_element_by_css_selector(tmp_css_selector).click()
            # select school
            driver.find_element_by_xpath('//*[@id="content"]/div[4]/div[1]/div/div/div/form/div[3]/button[2]').click()
            # save button
            time.sleep(2)


def p_name_process(text):
    p_name = text
    if '(' in p_name:
        p_name = p_name.split("(", 1)[0]
    if '（' in p_name:
        p_name = p_name.split("（", 1)[0]
    if '·' in p_name:
        p_name = p_name.split("·", 1)[1]
    return p_name.strip()


def selector_recursion(name_list, loc, selector, except_list=[]):
    # selector format: div#class1:a#class2
    arr = selector.split(":", 1)
    first = arr[0].split("#")
    # print(first)
    tag_name = first[0]
    if len(first) == 1 or first[1] == '':
        class_name = ""
    else:
        class_name = first[1]

    if len(arr) == 1:
        # final selector format: tag_name#class_name
        if class_name:
            for sub_loc in loc.find_all(tag_name, class_=class_name):
                p_name = p_name_process(sub_loc.text)
                if (except_list and p_name in except_list) or not p_name:
                    continue
                name_list.append(p_name)
        else:
            for sub_loc in loc.find_all(tag_name):
                p_name = p_name_process(sub_loc.text)
                if (except_list and p_name in except_list) or not p_name:
                    continue
                name_list.append(p_name)
        return name_list
    else:
        if class_name:
            for sub_loc in loc.find_all(tag_name, class_=class_name):
                return selector_recursion(name_list, sub_loc, arr[1], except_list=except_list)
        else:
            for sub_loc in loc.find_all(tag_name):
                return selector_recursion(name_list, sub_loc, arr[1], except_list=except_list)


def get_dept_list(dept_list_link, selector, except_str=''):
    dept_list = []
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    r = session.get(dept_list_link, headers=headers)
    # r = session.get(dept_list_link)
    r.encoding = r.apparent_encoding
    if not r.status_code == 200:
        print(r.status_code)
        print(r.text)
        exit()
    # print(r.text)
    soup = BeautifulSoup(r.text, "html.parser")
    if except_str:
        except_list = except_str.split(',')
    else:
        except_list = []
    return selector_recursion(dept_list, soup, selector, except_list=except_list)


def get_dept_list_by_selenium(dept_list_link, css_selector, except_str=''):
    dept_list = []
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(executable_path=chrome_ADDR, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
      """
    })
    driver.get(dept_list_link)
    driver.implicitly_wait(30)  # 智能等待，直到网页加载完毕，最长等待时间为30s

    for item in driver.find_elements_by_class_name("m-cell-bd"):
        print(item.text)
        dept_list.append(item.text)
    if except_str:
        except_list = except_str.split(',')
    else:
        except_list = []

    for item in driver.find_elements_by_css_selector(css_selector):
        dept_name = item.text
        p_name_process(item.text)
        if (except_list and dept_name in except_list) or not dept_name:
            continue
        dept_list.append(dept_name)
    return dept_list


list = [['南京航空航天大学', 'NUAA', 'http://nuaa.edu.cn/xysz/list.htm', 'div#paging_content:a', '继续教育,正德学院,金城学院'],
        # ['南京师范大学', 'NNU', 'http://www.njnu.edu.cn/xysz.htm', 'div#collegeEr:a', ''],
        ['南京艺术学院', 'NUA', 'https://www.nua.edu.cn/31/list.htm', 'div#paging_content:a', '体育部挂靠,附属中专'],
        ['南京传媒学院', 'CUCN', 'http://www.cucn.edu.cn/zzjs', 'section#specialMod:dt', ''],
        ['南京工业大学浦江学院', '南工浦江', 'https://www.njpji.cn/cmscontent/583.html', 'div#p_articles:a', ''],
        # ['南京理工大学', 'NJUST', 'https://www.njust.edu.cn/xysz/list.htm', 'div#content_column:a', '']
        ['河海大学', 'HHU', 'https://www.hhu.edu.cn/191/list.htm', 'div#wp_articlecontent:a', '信息学部'],
        ['南京医科大学', 'NMU', 'https://www.njmu.edu.cn/574/list.htm', 'div#wp_articlecontent:a', ''],
        ['南京工业大学', '南工', 'http://www.njtech.edu.cn/jgsz/xy.htm', 'table#table:a', ''],
        # ['南京林业大学', 'NJFU', '']
        ]

selenium_list = [
    ['南京师范大学', 'NNU', 'http://www.njnu.edu.cn/xysz.htm', 'h3.m-cell-bd', ''],
    ['南京理工大学', 'NJUST', 'https://www.njust.edu.cn/xysz/list.htm', 'ul.list-paddingleft-2>a', ''],
    # ['南京林业大学', 'NJFU', '']
]
#db_inputer = DataInputer()
#db_inputer.db_login()
for item in selenium_list:
    dept_list = get_dept_list_by_selenium(dept_list_link=item[2], css_selector=item[3], except_str=item[4])
    #dept_list = get_dept_list(dept_list_link=item[2], selector=item[3], except_str=item[4])
    print(dept_list)
    # db_inputer.each_input_db(dept_list, uni_name=item[0], uni_abbr=item[1])
