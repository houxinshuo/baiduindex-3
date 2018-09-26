from selenium import webdriver
import time
import pickle
import pandas as pd
from selenium.webdriver import ActionChains
from tqdm import tqdm

keyword = '甄嬛传'
chromedrivepath = 'E:\chromedriver\chromedriver.exe'

time_period = 0.5  # 控制每次获取数据的间隔，防止卡顿

browser = webdriver.Chrome(chromedrivepath)


def openbrowser():
    url = "http://index.baidu.com/"
    browser.maximize_window()
    browser.get(url)
    # 点击网页的登录按钮  browser.find_element_by_xpath("//ul[@class='usernav']/li[4]").click()
    # 完成登陆后在控制台输入1
    jud = input('第一次登陆？y/n：')
    if jud == 'y':
        jud2 = input("登录好后输入1：")
        while 1:
            if jud2 == '1':
                break
        pickle.dump(browser.get_cookies(), open("cookies.pkl", 'wb'))
    else:
        cookies = pickle.load(open("cookies.pkl", "rb"))  # 读取之前登录的cookies
        for cookie in cookies:  # 利用cookies进行登录
            browser.add_cookie(cookie)


def getindex(keyword, time_period):
    browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[1]/div/div[2]/form/input[3]").clear()
    # 写入需要搜索的百度指数
    browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[1]/div/div[2]/form/input[3]").send_keys(keyword)
    # 点击搜索
    try:
        browser.find_element_by_xpath("/html/body/div/div[2]/div[2]/div/div[1]/div/div[2]/div/span").click()
    except:
        browser.find_element_by_id("schsubmit").click()
    time.sleep(2)

    data_values = ['all', 'pc', 'wise']
    indexs = []
    for data_value in data_values:
        data_value_selector = browser.find_element_by_xpath('//li[@data-value="' + data_value + '"]')
        data_value_selector.click()

        oneDaySelector = browser.find_element_by_class_name("chartselectHours")
        oneDaySelector.click()

        xoyelement = browser.find_elements_by_css_selector("#trend rect")[2]
        print('开始获取指数——' + data_value)

        x_0 = 22
        y_0 = 150
        index = []
        times = []
        day = 24
        time.sleep(0.5)
        # webdriver.ActionChains(driver).move_to_element().click().perform()
        # 只有移动位置xoyelement[2]是准确的
        for i in tqdm(range(day)):
            # 坐标偏移量???
            ActionChains(browser).move_to_element_with_offset(xoyelement, x_0, y_0).perform()

            # 构造规则
            x_0 += 52.78260869
            if i == 22:
                x_0 = 1210
            time.sleep(time_period)
            # <div class="imgtxt" style="margin-left:-117px;"></div>
            viewvalue = browser.find_element_by_xpath('//td[@class="view-value"]')
            date_time = browser.find_element_by_xpath('//div[@class="view-table-wrap"]')
            # print(viewvalue.text)
            # print(date_time.text)
            while viewvalue.text == '':
                ActionChains(browser).move_to_element_with_offset(xoyelement, x_0 + 52.78260869, y_0).perform()
                time.sleep(time_period)
                ActionChains(browser).move_to_element_with_offset(xoyelement, x_0, y_0).perform()
                time.sleep(time_period)
                viewvalue = browser.find_element_by_xpath('//td[@class="view-value"]')
                date_time = browser.find_element_by_xpath('//div[@class="view-table-wrap"]')

            index.append(int(viewvalue.text.replace(',', '')))
            times.append(date_time.text)
        indexs.append(index)

    df = pd.DataFrame(data={'all': indexs[0], 'pc': indexs[1], 'wise': indexs[2]}, index=times)
    df.to_csv(keyword + '.csv')


openbrowser()
keyword = input('请输入搜索关键字：')
time_period = float(input('请输入时间间隔：'))
getindex(keyword=keyword, time_period=time_period)
