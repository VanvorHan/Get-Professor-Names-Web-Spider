import re
import csv
import string
import requests
import pandas as pd

from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
from zhon.hanzi import punctuation as punc
from selenium.webdriver.support.ui import WebDriverWait

ALL_PUNC = punc + string.punctuation


def del_punctuation(text):
    text = re.sub(r'[{}]+'.format(ALL_PUNC), '', text)
    return text.strip()


def is_contains_chinese(strs):
    for _char in strs:
        if '\u4e00' <= _char <= '\u9fa5':
            return True
    return False


def keep_only_chinese(strs):
    pattern = re.compile(r'[^\u4e00-\u9fa5]+')
    return re.sub(pattern, "", strs)


def data_dic_parser(original_str):
    data_dic = {}
    lines = original_str.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        print("line: ", line)
        tmp_list = line.split(': ', 1)
        data_dic[tmp_list[0]] = "".join(tmp_list[1:])
    return data_dic


def ajax_request(base_url, host, referer, data_dic_str):
    url = base_url
    name_list = []
    headers = {
        'Host': host,
        'Referer': referer,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    data = data_dic_parser(data_dic_str)
    print(data)
    try:
        response = requests.post(url=url, data=data, headers=headers)
        # print(response.text)
        # print(response.status_code)
        if response.status_code == 200:
            json = response.json()
            items = json.get('data')
            for item in items:
                p_name = item.get('title')
                name_list.append(p_name)
            return name_list
    except requests.ConnectionError as e:
        print('Error', e.args)


def append_results(params, result_list, professor_names):
    user_name = params[0]
    school_name = params[1]
    depart_name = params[2]
    for p_name in professor_names:
        if len(p_name) <= 1:
            continue
        if '—' in p_name:
            p_name = p_name.split("—")[-1]
        if '(' in p_name:
            p_name = p_name.split("(", 1)[0]
        if '（' in p_name:
            p_name = p_name.split("（", 1)[0]
        if is_contains_chinese(p_name):
            p_name = keep_only_chinese(p_name)

        p_name = del_punctuation(p_name)
        filters = ['姓名', '某某某', '教授', '副教授', '讲师', '', '\n', '\n\n', '\n\n\n']
        compare_list = [p_name == x for x in filters]
        if any(compare_list):
            continue
        # print(tmp)
        row = [user_name, school_name, p_name, depart_name]
        print(p_name)
        result_list.append(row)

    return result_list


def write_into_xls(result_list):
    with open('professor.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(result_list)

    read_file = pd.read_csv(r'professor.csv')
    read_file.to_excel(r'professor.xls', index=None, header=True)


def get_professor_txt(params, source_file="input.txt"):
    result_list = []
    f = open(source_file, "r")
    source_str = f.read()
    p_list = source_str.split(",")
    result_list = append_results(params, result_list, p_list)
    print(result_list)
    write_into_xls(result_list)


def get_professor_by_selenium(link):
    chrome_ADDR = '/Users/vanvorhan/Desktop/SchoolSpider/chromedriver'

    options = webdriver.ChromeOptions()
    options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    # 不加载图片,加快访问速度
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium

    driver = webdriver.Chrome(executable_path=chrome_ADDR, options=options)
    wait = WebDriverWait(driver, 10)  # 超时时长为10s

    driver.get(link)
    driver.implicitly_wait(30)  # 智能等待，直到网页加载完毕，最长等待时间为30s

    name_list = []
    for page_num in range(14):
        driver.switch_to.frame(driver.find_element_by_xpath('//*[@id="myiframe"]'))
        # ul = driver.find_element_by_xpath('//*[@id="teacherDiv"]/ul')
        for item in driver.find_elements_by_class_name("t-title"):
            print(item.text)
            name_list.append(item.text)
        driver.find_element_by_class_name("next").click()
        driver.switch_to.default_content()
    return name_list


def selector_recursion(name_list, loc, selector):
    # selector format: div#class1:a#class2
    arr = selector.split(":", 1)
    first = arr[0].split("#")
    print(first)
    tag_name = first[0]
    if len(first) == 1 or first[1] == '':
        class_name = ""
    else:
        class_name = first[1]

    if len(arr) == 1:
        # final selector format: tag_name#class_name
        if class_name:
            for sub_loc in loc.find_all(tag_name, class_=class_name):
                p_name = sub_loc.text
                name_list.append(p_name)
        else:
            for sub_loc in loc.find_all(tag_name):
                p_name = sub_loc.text
                name_list.append(p_name)
        return name_list
    else:
        if class_name:
            for sub_loc in loc.find_all(tag_name, class_=class_name):
                return selector_recursion(name_list, sub_loc, arr[1])
        else:
            for sub_loc in loc.find_all(tag_name):
                return selector_recursion(name_list, sub_loc, arr[1])


def get_professor(params, link, selector=None, use_ajax=False, use_selenium=False, data_dic_str=None, special=False, cookie=""):
    result_list = []
    if special:
        name_list = []
        session = requests.session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        r = session.get(link, headers=headers)
        r.encoding = r.apparent_encoding
        if not r.status_code == 200:
            print(r.status_code)
            exit()
        # print(r.text)
        soup = BeautifulSoup(r.text, "html.parser")

        for t in soup.find_all("table", class_="wp_editor_art_table"):
            for td in t.find_all("td"):
                for a in td.find_all("a", limit=1):
                    p_link = a.attrs['href']
                    if p_link == 'http://jszy.seu.edu.cn/_s1183/main.psp':
                        continue
                    get_professor(params, selector="td#infotitle", link=p_link)
                # p_name = a.text
                # name_list.append(p_name)
            # print(p_name)
        # print(name_list)
        # selector format: div#class1:a#class2

        # main = soup.find("div", class_='right')
    elif use_selenium:
        name_list = get_professor_by_selenium(link)
    elif use_ajax:
        if not data_dic_str:
            print("data_dic_str required")
            exit()
        o = urlparse(link)
        host = o.hostname
        base_url = "https://" + host + "/_wp3services/generalQuery?queryObj=teacherHome"
        name_list = ajax_request(base_url=base_url, host=host, referer=link, data_dic_str=data_dic_str)
        # print(data)
    else:
        name_list = []
        session = requests.session()
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en,zh-CN;q=0.9,zh-TW;q=0.8,zh;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cookie": cookie,
        }
        r = session.get(link, headers=headers)
        r.encoding = r.apparent_encoding
        if not r.status_code == 200:
            print(r.status_code)
            exit()
        # print(r.text)
        soup = BeautifulSoup(r.text, "html.parser")

        if not selector:
            print("selector required")
            exit()

        # selector format: div#class1:a#class2
        name_list = selector_recursion(name_list, soup, selector)

        '''for item in soup.select(selector):
            name_list.append(item.text)
            print(item.text)'''
    # print(name_list)
    result_list = append_results(params, result_list, name_list)
    print(result_list)
    write_into_xls(result_list)


def get_professor_multi_faculty(params, link, fac_selector, p_selector, cookie=""):
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en,zh-CN;q=0.9,zh-TW;q=0.8,zh;q=0.7",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": cookie,
    }
    r = session.get(link, headers=headers)
    r.encoding = r.apparent_encoding
    if not r.status_code == 200:
        print(r.status_code)
        exit()
    # print(r.text)
    soup = BeautifulSoup(r.text, "html.parser")

    if not fac_selector or not p_selector:
        print("selector required")
        exit()

    # selector format: div#class1:a#class2
    name_list = selector_recursion(name_list, soup, selector)

user_name = "maw"
school_name = "南京航空航天大学"
school_abbv = "（NUAA）"

dept_name = "自动化学院" + school_abbv
params = [user_name, school_name, dept_name]
'''
user_name = params[0]
school_name = params[1]
depart_name = params[2]
'''
#link = "https://cyber.seu.edu.cn/18201/list.htm"

dept_list =[["理学院", "http://science.nuaa.edu.cn/6623/list.htm", "div#wp_articlecontent:a", "ioGBNZZUiF6NS=5EAXjEcZMBcUaF7lw8LnstXlnmAy43DD4WmGV5kp9JpAXgUYvFYXFZ4JwbZbRIGTNpL74ouv7kWLUSqvuktaqdA; JSESSIONID=FF62C72446C539581952690D16FFAE38; ioGBNZZUiF6NT=53XJJ6ChOs83qqqDcp5GCPGej9s4w8.QyuM46o0ZGyY5603wSQ2cTVzKaP3Hvt9BdpM6951YmcGLU.iYCf7LnOw8DgbfMXMps9qlEwUMhjvAGxZf3JXi2HubD2F7oMDTV_3zwU9fJu9R_B5Pk1GpPeNXQMUdhyXjOWTC2x0tySEnO.rozu6pOJIGJyME9DOdN_1pdebjwrrBE.3X5OdFvVeHV8wTegXRJpefKyuHjpOCBfcTGivFUCzVIBrlzxLZkwCGdNtIgNiaQ.BnfBce4WI7MLppEMx4JT6sjaPZIQ8mq"],
              ]

for dept in dept_list:
    dept_name = dept[0] + school_abbv
    params = [user_name, school_name, dept_name]
    #get_professor(params, selector=dept[2],link=dept[1], cookie=dept[3])
    get_professor_txt(params)


links = []

data_dic_str = '''siteId: 38
pageIndex: 1
rows: 999
conditions: [{"field":"published","value":"1","judge":"="}]
orders: [{"field":"letter","type":"asc"},{"field":"published","type":"1"}]
returnInfos: [{"field":"title","name":"title"},{"field":"cnUrl","name":"cnUrl"},{"field":"headerPic","name":"headerPic"},{"field":"exField1","name":"exField1"},{"field":"exField2","name":"exField2"},{"field":"exField5","name":"exField5"},{"field":"career","name":"career"},{"field":"post","name":"post"}]
articleType: 1
level: 1
'''
'''for link in links:
    get_professor(params, selector="div#txt", link=link, use_ajax=False, data_dic_str=data_dic_str)'''
#get_professor_txt(params)

# link = "https://life.nju.edu.cn/szdw/list.htm"
# get_professor(params, link=link, use_ajax=True, data_dic_str=data_dic_str)