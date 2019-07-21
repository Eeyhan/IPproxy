#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : proxy.py


import gevent
from gevent import monkey

monkey.patch_all()  # 如果是开启进程池需要把这个注释掉
import abc
import json
import re
import asyncio
import requests
from lxml import etree
from bs4 import BeautifulSoup
import random
from functools import reduce
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import time
from multiprocessing import Pool
from config import TEST_PROXY_URLS, PROXY_URLS, USER_AGENT


class BaseProxy(object):
    """获取代理IP"""

    def __init__(self):
        self.header = None
        self.proxy_list = []
        self.proxy_dict = {}
        self.user_agent = USER_AGENT
        self.header = self.get_header
        self.test_proxy_urls = TEST_PROXY_URLS

        # 节省创建对象的资源
        self.proxy_urls = self.get_proxy_site

    def request_user_agent(self):
        """
        预留的钩子函数，返回的值可以由子类自定制
        :return: 返回user-agent
        """
        return self.user_agent

    @property
    def get_proxy_site(self):
        """
        预留的钩子函数，返回的值可以由子类自定制
        :return:
        """
        return self.request_proxy_urls()

    def request_proxy_urls(self):
        """
        获取代理站点，重新拼接字段
        :return: 返回代理ip地址
        """
        # proxy_url_list = Queue()
        proxy_url_list = []
        for item in PROXY_URLS:
            item['type'] = 'parser_' + item['type']
            proxy_url_list.append(item)
        self.proxy_urls = proxy_url_list
        return self.proxy_urls

    def request_test_proxy_url(self):
        """
        预留的钩子函数，返回的值可以由子类自定制
        :return:
        """
        return self.test_proxy_urls

    @property
    def get_header(self):
        """
        :return: 返回构造好的header头信息
        """
        user_agent = self.request_user_agent()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': random.choice(user_agent),
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
        }
        return headers

    def request_common_url(self, url, url_name=None, proxy=False):
        """
        访问网站的通用方法
        :param url: 网站链接
        :param url_name: 请求代理网站时的别名，如果是测试代理不传入该值
        :param proxy: 代理参数
        :return:
        """

        headers = self.header
        headers['Referer'] = url
        headers['Host'] = url.split('/')[2]
        headers['Connection'] = 'close'
        res = None
        try:
            if not proxy:
                res = requests.get(url, headers=self.header)
            else:
                res = requests.get(url, headers=headers, proxies=proxy)
        except Exception as e:
            print(e)
        # 根据获取到的编码方式解码

        if not res or res.status_code != 200:
            raise Exception('网络请求超时或者请求被拒绝')
        try:
            html = res.content.decode('utf-8')
        except Exception as e:
            print(e)
            html = res.content.decode('gb2312')
        if url_name.startswith('parser'):
            self.parser(html, url_name)
        elif url_name.startswith('test'):
            result = self.test_parser(html, url_name, proxy)
            return result
        else:
            return

    def compare_proxy(self, proxy, current_ip):
        """
        拆分代理，只要ip:port
        :param proxy:爬取的代理ip
        :param current_ip: IP查询网站显示的ip
        :return:
        """

        proxy_ip = list(proxy.values())[0].split('//')[1]
        if current_ip in proxy_ip:  # current_ip:x.x.x.x proxy_ip:x.x.x.x:xx
            return True
        return

    def request_site(self, proxy_urls):
        """
        获取代理网站的源码数据
        :return:
        """
        task = []
        for item in self.proxy_urls:
            url = item.get('url')
            url_name = item.get('type')
            task.append(gevent.spawn(self.request_common_url, url, url_name, False))
        gevent.joinall(task)

    def parser(self, html, url_name):
        """
        分发解析器
        :param html: 拿到的网站源码
        :param url_name: 请求的代理网站别名
        :return:
        """
        func = getattr(self, url_name)
        # 如果对象存在对应解析方法
        if func:
            # 如果是goubanjia，用BeautifulSoup解析
            if url_name == 'parser_goubanjia':
                html = BeautifulSoup(html, "lxml")
                func(html)
            # 其余用xpath解析
            else:
                html = etree.HTML(html)
                func(html)

    def test_parser(self, html, url_name, proxy):
        func = getattr(self, url_name)
        if func:
            result = func(html, proxy)
            return result

    def parser_xici(self, etree_html):
        """
        西刺代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//table/tr[position()>1]')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            # print(xpath_data)
            ip = xpath_data[0]
            port = xpath_data[1]
            ip_port = ip + ':' + port
            protocal_1 = xpath_data[4].lower()
            protocal_2 = xpath_data[5].lower()
            protocal = protocal_1 if 'http' in protocal_1 else protocal_2

            # 如果还是没有http字样，那就是qq代理
            if 'http' not in protocal:
                protocal = protocal_1 if 'qq' in protocal_1 else protocal_2
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_kuaidaili(self, etree_html):
        """
        快代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//*[@id="list"]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0]
            port = xpath_data[1]
            ip_port = ip + ':' + port
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_kuaidaili_new(self, etree_html):
        """
        快代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//tr')[10:]
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0]
            port = xpath_data[1]
            ip_port = ip + ':' + port
            protocal = xpath_data[3]
            protocal = 'https' if 'HTTPS' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_89ip(self, etree_html):
        """
        89代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//table[@class="layui-table"]/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0].replace('\n', '').replace('\t', '')
            port = xpath_data[1].replace('\n', '').replace('\t', '')
            ip_port = ip + port
            self.proxy_list.append({'http': 'http://' + ip_port})
            # self.proxy_dict.update({'http': 'http://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_qydaili(self, etree_html):
        """
        齐云代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//*[@id="content"]/section/div[2]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0]
            port = xpath_data[1]
            ip_port = ip + ':' + port
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_3366(self, etree_html):
        """
        3366代理解析
        :param etree_html: etree对象
        :return:
        """
        res = etree_html.xpath('//*[@id="list"]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0]
            port = xpath_data[1]
            ip_port = ip + ':' + port
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_ihuan(self, etree_html):
        """小幻代理，访问过于频繁的话会限流"""
        res = etree_html.xpath('//div[@class="table-responsive"]/table/tbody/tr')
        for item in res:
            ip = item.xpath('string(./td)')
            xpath_data = item.xpath('./td/text()')
            port = xpath_data[0]
            ip_port = ip + ':' + port
            protocal = 'https' if xpath_data[3] == '支持' else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_xila(self, etree_html):
        """西拉代理解析"""
        res = etree_html.xpath('//table[@class="fl-table"]/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0]
            protocal = xpath_data[1].lower()
            protocal = 'https' if 'https' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_iphai(self, etree_html):
        """ip海代理"""
        res = etree_html.xpath('//table/tr[position()>1]')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip = xpath_data[0].strip()
            port = xpath_data[1].strip()
            ip_port = ip + ':' + port
            protocal = xpath_data[3].strip().lower()
            protocal = 'https' if 'https' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def get_goubanjia_port(self, port_word):
        """
        解密goubanjia真实端口号
        :param port_word: 加密字段
        :return:
        """
        word = list(port_word)
        num_list = []
        for item in word:
            num = 'ABCDEFGHIZ'.find(item)
            num_list.append(str(num))
        # print(int("".join(num_list)))
        port = int("".join(num_list)) >> 0x3
        # print(port)
        return port

    def parser_goubanjia(self, html):
        """
        解析goubanjia代理
        :param html: 网站源码
        :return:
        """
        soup = html.select('tr')[1:]
        prototal_list = []
        temp_list = []
        for item in soup:
            a_list = item.select('td > a')
            for a in a_list:
                if 'http' in a or 'https' in a:
                    protocal = a.string
                    prototal_list.append(protocal)
            td_list = item.select('td[class="ip"]')
            for td in td_list:
                child_list = td.find_all()
                text = ""
                for child in child_list:
                    if 'style' in child.attrs.keys():
                        if child.attrs['style'].replace(' ', '') == "display:inline-block;":
                            if child.string != None:
                                text = text + child.string
                    # 过滤出端口号
                    elif 'class' in child.attrs.keys():
                        class_list = child.attrs['class']
                        if 'port' in class_list:
                            port = self.get_goubanjia_port(class_list[1])
                            # 拼接端口
                            text = text + ":" + str(port)
                    else:
                        if child.string != None:
                            text = text + child.string
                temp_list.append(text)
        data = zip(prototal_list, temp_list)
        for item in data:
            self.proxy_list.append({item[0]: item[0] + '://' + item[1]})
            # self.proxy_dict.update({item[0]: item[0] + '://' + item[1]})
        # print(proxy_list)
        return self.proxy_list

    def parser_feiyi(self, html):
        """
        飞蚁代理解析
        :param html:etree对象
        :return:
        """
        res = html.xpath('//table/tr[position()>1]')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0] + ':' + xpath_data[1]
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list)
        return self.proxy_list

    def parser_shenji(self, html):
        """
        神鸡代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//table/tr[position()>1]')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0]
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_mipu(self, html):
        """
        米扑代理解析 该方法未完善，后续补充
        :param html: etree对象
        :return:
        """
        ip_ports = html.xpath('//td[@class="tbl-proxy-ip"]')
        protocals = html.xpath('//td[@class="tbl-proxy-type"]')
        for item in ip_ports:
            xpath_data = item.xpath('string(.)')
            print(xpath_data)
        for item in protocals:
            xpath_data = item.xpath('string(.)')
            print(xpath_data)

        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_kaixin(self, html):
        """
        开心代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//*[@id="nav_btn01"]/div[6]/table/tbody/tr')
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0] + ':' + xpath_data[1]
            protocal = xpath_data[3].lower()
            protocal = 'https' if 'https' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_jisu(self, html):
        """
        极速代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//tr')[5:]
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0] + ':' + xpath_data[1]
            protocal = xpath_data[3].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_jxl(self, html):
        """
        jxl代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//table/tbody/tr')
        # print(len(res))
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[1] + ':' + xpath_data[2]
            protocal = xpath_data[4].lower()
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_cross(self, html):
        """
        cross代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//table/tr[position()>1]')
        # print(len(res))
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0] + ':' + xpath_data[1]
            protocal = xpath_data[4].lower()
            protocal = 'https' if 'https' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_nima(self, html):
        """
        尼玛代理解析
        :param html: etree对象
        :return:
        """
        res = html.xpath('//table/tbody/tr')
        # print(len(res))
        for item in res:
            xpath_data = item.xpath('./td/text()')
            ip_port = xpath_data[0]
            protocal = xpath_data[1].lower()
            protocal = 'https' if 'https' in protocal else 'http'
            self.proxy_list.append({protocal: protocal + '://' + ip_port})
            # self.proxy_dict.update({protocal: protocal + '://' + ip_port})
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def choice_test_site(self, proxy):
        test_url = random.choice(TEST_PROXY_URLS)
        url = test_url.get('url')
        url_name = 'test_' + test_url.get('type')
        result = self.request_common_url(url, url_name, proxy)
        return result

    def get_test_proxy(self, proxy=None):
        """
        测试代理是否成功
        :param proxy: 代理，如果为None则自动萱蕚
        :return: 成功返回True,失败范围False
        """
        if not proxy:
            proxy = random.choice(self.proxy_list)

        result = self.choice_test_site(proxy)
        if result:
            return result  # proxy

        # 递归查找，直到有正常数据返回
        self.get_test_proxy(proxy)

    @property
    def proxy(self):
        result = self.get_test_proxy()
        return result

    def proxy_duplicate_removal(self):
        """
        对爬取到的数据去重
        :return:
        """
        proxy_list = lambda x, y: x if y in x else x + [y]
        self.proxy_list = reduce(proxy_list, [[], ] + self.proxy_list)
        return self.proxy_list

    def get_proxy(self, url=None):
        """
        获取最终的结果
        :param url: 代理网站
        :return:
        """
        self.request_site(proxy_urls=url)
        # 去重
        self.proxy_list = self.proxy_duplicate_removal()

        print('已爬取代理 %s 个' % len(self.proxy_list))
        return self.proxy_list

    @property
    def proxys(self):
        """
        入口方法，返回代理数组
        :return:
        """
        result = self.get_proxy()
        return result

    def test_httpbin(self, html, proxy):
        """
        httpbin的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = json.loads(html)
        current_ip = html.get('origin')
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_chinaz(self, html, proxy):
        """
        chinaz的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//*[@id="rightinfo"]/dl/dd[1]/text()')[0]
        result = self.compare_proxy(proxy, current_ip)

        if result:
            return proxy

    def test_ipip(self, html, proxy):
        """
        ipip的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//input/@value')[0]
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_ipcn(self, html, proxy):
        """
        ipcn的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//div[@id="result"]/div/p[1]/code/text()')
        print(current_ip)
        time.sleep(10000)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_luip(self, html, proxy):
        """
        luip的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//*[@id="ipaddress"]/text()')[0]
        print(current_ip)
        time.sleep(1000)


    def test_sohu(self, html, proxy):
        """
        搜狐网的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = html.split('=')[1].replace(';', '')
        html = json.loads(html)
        current_ip = html.get('cip')
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_onlineservice(self, html, proxy):
        """
        onlineservice的IP查询
        :param html: 该网站较特殊，此时的html就是返回IP
        :param proxy: 待测试的代理IP
        :return:
        """
        result = self.compare_proxy(proxy, html)
        if result:
            return proxy

    def test_ttt(self, html, proxy):
        """
        ttt的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//*[@id="getip"]/text()')[0]
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_taobao(self, html, proxy):
        """
        ttt的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        html = etree.HTML(html)
        current_ip = html.xpath('//*[@id="obviousIp"]/text()')[0]
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy


class NormalProxy(BaseProxy):
    # def get_test_proxy(self, proxy=None):
    #     """
    #     测试代理是否成功
    #     :param proxy: 代理
    #     :return: 成功返回True,失败范围False
    #     """
    #     # url = 'http://httpbin.org/ip'
    #     url = 'https://www.ipip.net/ip.html'
    #     # 表示测试爬取的所有结果
    #     # 待测试的代理
    #     testing_proxy = []
    #     tested_proxy = []  # 已测试的代理
    #     for item in self.proxy_list:
    #         if 'qq代理' not in item.keys():
    #             testing_proxy.append(item)
    #         else:
    #             tested_proxy.append(item)
    #     tasks = []
    #     for proxy in testing_proxy:
    #         tasks.append(gevent.spawn(self.request_common_url, url, None, proxy))
    #     gevent.joinall(tasks)

    pass


class ThreadProxy(BaseProxy):

    def request_site(self, proxy_urls):
        """
        获取代理网站的源码数据,单个url的方式
        :return:
        """
        url = proxy_urls.get('url')
        url_name = proxy_urls.get('type')
        self.request_common_url(url, url_name, False)


def proxy_duplicate_removal(lists):
    """
    对爬取到的数据去重
    :return:
    """
    proxy_list = lambda x, y: x if y in x else x + [y]
    return reduce(proxy_list, [[], ] + lists)


def main_gevent():
    # 利用协程一般保持在13秒，记得monkey打补丁
    res = NormalProxy()
    print(len(res.proxys))
    proxy_list = res.proxys
    proxy_list = proxy_duplicate_removal(proxy_list)
    # print(proxy_list)
    available_proxy = res.proxy
    return available_proxy


def main_thread_pool():
    # 利用协程一般保持在8-13秒
    res = ThreadProxy()
    thread = ThreadPoolExecutor()
    tasks = [thread.submit(res.get_proxy, url) for url in PROXY_URLS]
    thread.shutdown()
    temp_data = [obj.result() for obj in as_completed(tasks)]
    data = []
    for item in temp_data:
        data.extend(item)
    proxy_list = proxy_duplicate_removal(data)
    print(proxy_list)
    print(len(proxy_list))
    return proxy_list


def main_process_pool():
    res = ThreadProxy()
    tasks = []
    process = ProcessPoolExecutor(max_workers=3)
    for url in PROXY_URLS:
        obj = process.submit(res.get_proxy, url).result()
        tasks.append(obj)
    process.shutdown()
    proxy_list = [obj.result() for obj in tasks]
    print(len(proxy_list))
    return proxy_list


def main_thread_pool_asynicio():
    res = ThreadProxy()
    loop = asyncio.get_event_loop()
    thread = ThreadPoolExecutor()
    tasks = [loop.run_in_executor(thread, res.get_proxy, url) for url in PROXY_URLS]
    loop.run_until_complete(asyncio.wait(tasks))
    proxy_list = []
    for obj in tasks:
        proxy_list.extend(obj.result())
    # 异步操作会有重复的数据,去重
    proxy_list = proxy_duplicate_removal(proxy_list)
    print(len(proxy_list))
    print(proxy_list)
    return proxy_list


if __name__ == '__main__':
    start = time.time()
    # 第一版，使用协程
    main_gevent()

    # 第二版，使用线程池
    # main_thread_pool()

    # 第三版，使用线程池+异步io
    # main_thread_pool_asynicio()

    print(time.time() - start)
