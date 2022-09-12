#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import re
import sys
import requests
import datetime
import subprocess
import shutil
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import json
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.utils import ChromeType

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }

workingMode = 1 # mhtml mode
while True:
    currPath = os.path.dirname(os.path.realpath(__name__))
    tempFilesPath = os.path.join(currPath, "TempFiles")

    if not os.path.exists(tempFilesPath):
        os.makedirs(tempFilesPath)
        print("建立TempFiles文件夹。")
    if not os.path.exists(tempFilesPath):
        print("找不到TempFiles文件夹，请检查工作文件夹的权限要求。")
    
    if workingMode == 1:
        url = input("\nmhtml模式；请输入豆瓣帖子网址(类似：https://www.douban.com/group/topic/########)\n(输入2进入html模式或输入Q退出)：\n")
        if url.startswith(('Q', 'q')):
            break
        elif url == '1':
            continue
        elif url == '2':
            workingMode = 2 # html mode
            continue
        elif 'douban.com/group/topic' not in url:
            print("网址不正确，请检查。")
            continue
    elif workingMode ==2:
        url = input("\nhtml模式；请输入豆瓣帖子网址(类似：https://www.douban.com/group/topic/########)\n(输入1进入mhtml模式或输入Q退出)：\n")
        if url.startswith(('Q', 'q')):
            break
        elif url == '1':
            workingMode = 1 # mhtml mode
            continue
        elif url == '2':
            continue
        elif 'douban.com/group/topic' not in url:
            print("网址不正确，请检查。")
            continue



    r = requests.get(url=url, headers=headers)
    html_str = r.text
    title_result = re.findall('<title>([\s\S]*?)</title>', html_str)
    title = re.findall('\s*(.+)', title_result[0])
    postID = re.findall('topic/(\d+)', url)[0]
    with open("TempFiles/Temp1.html", 'w', encoding="utf-8") as fw:
        fw.write(html_str)

    remove_items = ['id="db-global-nav"', 'id="db-nav-group"', 'id="landing-bar"', 'class="top-nav-doubanapp"', 'id="doubanapp-tip"', 'id="top-nav-appintro"', 'class="global-nav-items"']  

    # 打开文件
    temp1_file = os.path.join(currPath, "TempFiles", "temp1.html")
    temp2_file = os.path.join(currPath, "TempFiles", "temp2.html")
    with open(temp1_file, 'r', encoding="utf-8") as f:
        with open(temp2_file, 'w', encoding="utf-8") as fw:
            for line in f:
                if any(i in line for i in remove_items):
                    while line != "</div>\n":
                        line = f.readline()
                    continue

                line = re.sub('data-original-url="(.*?)"([\s\S]*?)data-render-type="gif"([\s\S]*?)src=".*?"', 'data-original-url="\\1"\\2\\3src="\\1"', line)
                line = line.replace('class="cmt-img"', 'class="cmt-img cmt-img-large"')
                line = line.replace('style="margin-top', 'raw-style="margin-top')
                line = re.sub('(src=".*?)richtext/l/public(.*?alt="")', '\\1richtext/raw/public\\2', line)
                line = re.sub('( *?)data-render-type="gif"\n', '', line)
                fw.write(line)

    url_page_no = re.findall('.+start=(\d+)', url)
    if url_page_no == []:
        page_no = "第01页"
    else:
        page_no = "第" + "{:0>2d}".format(int(int(url_page_no[0])/100) + 1) + "页"

    if workingMode == 2:
        now = str(datetime.datetime.now())[:19]
        now = now.replace(":","_")
        dst_file = title[0] + '_' + postID + '_' + page_no + '(' + str(now) + ").html"
        shutil.copy(temp2_file,dst_file)
        if os.path.exists(dst_file):
            print("运行结束，得到->" + dst_file)
            print('请用浏览器打开并另存为mhtml。')
        continue


    # 此部分主要參考自https://blog.csdn.net/gjbfyhbfg/article/details/104845780
    # 加启动配置    
    chromeOptions = webdriver.ChromeOptions()
    # 打开chrome浏览器
    # 此步骤很重要，设置为开发者模式，防止被各大网站识别出来使用了Selenium
    # chromeOptions.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志
    chromeOptions.add_experimental_option('excludeSwitches', ['enable-automation'])#跟上面只能选一个
    chromeOptions.add_argument('--start-maximized')#最大化
    chromeOptions.add_argument('--incognito')#无痕隐身模式
    chromeOptions.add_argument("disable-cache")#禁用缓存
    chromeOptions.add_argument('disable-infobars')
    chromeOptions.add_argument('log-level=3')#INFO = 0 WARNING = 1 LOG_ERROR = 2 LOG_FATAL = 3 default is 0
    chromeOptions.add_argument('--headless')         # 谷歌无头模式
    chromeOptions.add_argument('--disable-gpu')       # 禁用显卡
    chromeOptions.add_argument('window-size=1280,1000')  # 指定浏览器分辨率
    chromeOptions.add_argument('--enable-webgl')
    chromeOptions.add_argument("--no-sandbox")
    chromeOptions.add_argument('--disable-dev-shm-usage')
    
    
    chromeDriverPath = os.path.join(currPath, "chromedriver", "chromedriver.exe")
    # with webdriver.Chrome(service=Service(ChromeDriverManager().install()), executable_path=chromeDriverPath, options=chromeOptions) as driver:        
    with webdriver.Chrome(service=Service(executable_path=chromeDriverPath), options=chromeOptions) as driver:
        print("运作中，请稍候")
        now = str(datetime.datetime.now())[:19]
        now = now.replace(":","_")
        dst_file = title[0] + '_' + postID + '_' + page_no + '(' + str(now) + ").mhtml"
        driver.get(temp2_file)
        
        # 1. 执行 Chrome 开发工具命令，得到mhtml内容
        res = driver.execute_cdp_cmd('Page.captureSnapshot', {})
        # 2. 写入文件
        with open(dst_file, 'w', newline='') as f:   # 根据5楼的评论，添加newline=''
            f.write(res['data'])
        if os.path.exists(dst_file):
            print("运行结束，请检查->" + dst_file)