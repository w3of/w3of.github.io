#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import urllib.parse
import urllib.request
import urllib.error

# 结果保存字典
result = {}
# 所有的关键词集合
has_seen = set()
# 待搜索集合
wait = set()

def download(url,timeout=5,user_agent='dyspider',proxy=None,num_retries=5):
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
    # print('Downloading:',url)
    try:
        # 打开网页并读取内容存入html变量中
        html = urllib.request.urlopen(request,timeout=timeout).read()
    except urllib.error.URLError as err:
        print('Download error:',err.reason)
        html = None # 如果有异常，那么html肯定是没获取到的，所以赋值None
        if num_retries > 0:
            if hasattr(err,'code') and 500 <= err.code <= 600:
                return download(url,timeout,user_agent,proxy,num_retries-1)
    return html

def extract(html):
    '''
    提取关键词
    :param html:HTML源码
    :return: 关键词列表
    '''
    search_res = re.search(r's:\[(.*?)\]',html,re.S)
    if search_res:
        search_res = search_res.group(1)
    else:
        search_res = ''
    return re.findall(r'"(.*?)"', search_res, re.S)

def filter_kw(key):
    global has_seen,wait,result
    if key not in has_seen: # 判断关键词是否在已抓取列表里面
        has_seen.add(key) # 如果没在就添加进去
        wait.add(key) # 同时添加进待抓取队列内
        result[key] = 1 # 同时添加到结果字典内，并统计关键词出现次数
    else:
        result[key] += 1


if __name__ == '__main__':
    ua = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ' \
         '(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    result['seo'] = 1
    has_seen.add('seo')
    wait.add('seo')
    while wait:
        # 中文路径处理：urllib.parse.quote()
        baidu_url = 'https://sp0.baidu.com/5a1Fazu8AA54nxGko9WTAnF6hhy/su?wd=%s' % urllib.parse.quote(wait.pop())
        source = download(baidu_url)
        # 如果网页因为某些原因（比如百度封IP了）返回值为None，那么就不存在编码问题，所以进行判断看需不需要加decode()
        if source:
            source = source.decode('gbk')
            kwlist = extract(source)
            for key in kwlist:
                filter_kw(key)
        print(result)
