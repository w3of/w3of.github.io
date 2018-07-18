#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib
from urllib import request,error,parse
import requests # 需要用pip命令安装requests模块
import time
import re
import random

uaList = ['Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 BIDUBrowser/8.7 Safari/537.36']
ua = random.choice(uaList)
key_url=[]
key_word=[]

def download(url,timeout=10,user_agent='dyspider',proxy=None,num_retries=5):
    """
    通用网页源码下载函数
    :param url: 要下载的url
    :param timeout: 请求超时时间，单位/秒。可能某些网站的反应速度很慢，所以需要一个连接超时变量来处理。
    :param user_agent: 用户代理信息，可以自定义是爬虫还是模拟用户
    :param proxy: ip代理(http代理)，访问某些国外网站的时候需要用到。必须是双元素元组或列表（‘ip：端口’，‘http/https’）
    :param num_retries: 失败重试次数
    :return: HTML网页源码
    """
    headers = {'User-Agent':user_agent}
    request = urllib.request.Request(url,headers=headers)
    if proxy: # 如果有代理值，可以通过set_proxy方法添加上
        proxy_host,proxy_type = proxy # 对proxy值进行解包
        request.set_proxy(proxy_host,proxy_type)
    print('Downloading:',url)
    try:
        # 打开网页并读取内容存入html变量中
        html = urllib.request.urlopen(request,timeout=timeout).read().decode('utf-8')
    except urllib.error.URLError as err:
        print('Download error:',err.reason)
        html = None # 如果有异常，那么html肯定是没获取到的，所以赋值None
        if num_retries > 0:
            if hasattr(err,'code') and 500 <= err.code <= 600:
                return download(url,timeout,user_agent,proxy,num_retries-1)
    return html

def createKey():   #create baidu URL with search words
    with open('关键词.txt') as f:
        for key in f:
            key_word.append(key)

if __name__ == '__main__':
    createKey()
    with open('PC-排名结果.txt', 'a', encoding='utf-8') as f:
        f.write('***********'+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'***********'+'\n')
    for k in key_word:
        t = 0
        key_url = parse.quote(k.strip())
        for p in range(0,41,10): # 第二个参数设置页数（前二页11，前三页21，前四页31，以此类推。）
            url = 'https://www.baidu.com/s?wd=%s&pn=%d&rn=10' % (key_url,p)
            html = download(url, user_agent=ua)
            a = re.findall(r'<div class="result c-container "(.*?)class="m">百度快照</a>', html, re.S | re.I)
            for i in a:
                b = re.search(r'data-tools=.*?{"title":".*?","url":"(.*?)"}.*?><a class="c-tip-icon">', i,
                              re.I | re.S).group(1)
                c = re.search(r'id="(.*?)".*?tpl="se.*?"', i, re.S | re.I).group(1)
                r = requests.head(b).headers['Location']
                with open('PC-排名结果.txt', 'a', encoding='utf-8') as f:
                    if 'seopeixun.com' in r: #这里指定需要检测的网址
                        line = k.strip() + '####第%s名：' % c + r + '\n'
                        f.write(line)
                        f.flush()
                        t = 1
                        break
                    else:
                        continue
            if t == 1:
                break
            else:
                continue
        if t==0:
            with open('PC-排名结果.txt', 'a', encoding='utf-8') as f:
                line = k.strip() + '####排名>50'+ '\n'
                f.write(line)
                f.flush()
    print('完成！')









