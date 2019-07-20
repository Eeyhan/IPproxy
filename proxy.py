#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : proxy.py


import gevent
from gevent import monkey

monkey.patch_all()  # 如果是开启进程池需要把这个注释掉
import abc
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
import selectors


# q = Queue()
# for item in PROXY_URLS:
#     q.put(item)
# print(q.get())


class BaseProxy(object):
    """获取代理IP"""

    def __init__(self):
        """
        :param url: ip代理网站的url路径
        :param url_name: ip代理网站名
        """

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

    # def request_url(self, url, proxy=False):
    #     """
    #     访问网站的通用方法
    #     :param url: 网站链接
    #     :param proxy: 代理参数
    #     :return:
    #     """
    #     if not proxy:
    #         res = requests.get(url, headers=self.header)
    #     else:
    #         res = requests.get(url, headers=self.header, proxies=proxy)
    #     # 根据获取到的编码方式解码
    #     html_charset = requests.utils.get_encodings_from_content(res.text)[0].lower()
    #     html = res.content.decode(html_charset)
    #     return html

    # def request_common_url(self, url, url_name=None, proxy=False):
    #     """
    #     访问网站的通用方法
    #     :param url: 网站链接
    #     :param url_name: 请求代理网站时的别名，如果是测试代理不传入该值
    #     :param proxy: 代理参数
    #     :return:
    #     """
    #     html = None
    #     res = None
    #     try:
    #         if not proxy:
    #             res = requests.get(url, headers=self.header)
    #         else:
    #             res = requests.get(url, headers=self.header, proxies=proxy)
    #     except Exception as e:
    #         print(e)
    #
    #     # 根据获取到的编码方式解码
    #     if not res:
    #         return
    #     if res.status_code == 200:
    #         # print(res.text)
    #         # print(requests.utils.get_encodings_from_content(res.text))
    #         # # html_charset = requests.utils.get_encodings_from_content(res.text)[0].lower()
    #         # # html = res.content.decode(html_charset)
    #         try:
    #             html = res.content.decode('utf-8')
    #         except Exception as e:
    #             print(e)
    #             html = res.content.decode('gb2312')
    #
    #         if url_name:
    #             self.parser(html, url_name)
    #         else:
    #             return res, html

    def request_common_url(self, url, url_name=None, proxy=False):
        """
        访问网站的通用方法
        :param url: 网站链接
        :param url_name: 请求代理网站时的别名，如果是测试代理不传入该值
        :param proxy: 代理参数
        :return:
        """
        res = None
        try:
            if not proxy:
                res = requests.get(url, headers=self.header)
            else:
                res = requests.get(url, headers=self.header, proxies=proxy)
        except Exception as e:
            print(e)
        # 根据获取到的编码方式解码
        if not res:
            return
        if res.status_code == 200:
            try:
                html = res.content.decode('utf-8')
            except Exception as e:
                print(e)
                html = res.content.decode('gb2312')
            if url_name:
                self.parser(html, url_name)
            else:
                print(html)
                self.get_testing_response(res, html)
                return res, html

    def get_testing_response(self, res, html):
        """
        获取测试IP的网站的结果
        :param res: 请求对象
        :param html: 源文件
        :return:
        """
        print(html)

    # def request_site(self):
    #     """
    #     获取代理网站的源码数据
    #     :return:
    #     """
    #     # html = self.request_url()
    #     # self.parser(html)
    #
    #     # 使用gevent协程
    #     task = []
    #     for item in self.proxy_urls:
    #         url = item.get('url')
    #         url_name = item.get('type')
    #         task.append(gevent.spawn(self.request_common_url, url, url_name, False))
    #     gevent.joinall(task)

    # def request_site_single(self, proxy_urls):
    #     """
    #     获取代理网站的源码数据,单个url的方式
    #     :param proxy_urls: 代理网站
    #     :return:
    #     """
    #     # html = self.request_url()
    #     # self.parser(html)
    #
    #     url = proxy_urls.get('url')
    #     url_name = proxy_urls.get('type')
    #     self.request_common_url(url, url_name, False)

    @abc.abstractmethod
    def request_site(self, proxy_urls):
        """
        获取网站
        :return:
        """
        pass

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

    # def get_test_proxy(self, proxy=None):
    #     """
    #     测试代理是否成功
    #     :param proxy: 代理
    #     :return: 成功返回True,失败范围False
    #     """
    #     url = 'http://httpbin.org/ip'
    #
    #     # 表示测试爬取的所有结果
    #     if not proxy:
    #         pass
    #
    #     testing_proxy = []  # 待测试的代理
    #     tested_proxy = []  # 已测试的代理
    #     for item in self.proxy_list:
    #         if 'qq代理' not in item.keys():
    #             testing_proxy.append(item)
    #
    #         # res, html = self.request_common_url(url=url, proxy=item)
    #         # if res
    #         # print(html)
    #         # html

    @abc.abstractmethod
    def get_test_proxy(self, proxy=None):
        """
        测试代理是否成功
        :param proxy: 代理
        :return: 成功返回True,失败范围False
        """
        pass

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

        # 测试代理，清洗数据
        print('...')
        self.get_test_proxy()
        print('...')
        # 去重
        self.proxy_list = self.proxy_duplicate_removal()
        print('已爬取代理 %s 个' % len(self.proxy_list))
        return self.proxy_list

    @property
    def proxy(self):
        """
        入口方法，返回代理列表
        :return:
        """

        result = self.get_proxy()
        return result

    def testing_httpbin(self, html, proxy):
        current_ip = html.get('origin')
        if list(proxy.values())[0] in current_ip:
            return True
        return

    def testing_chinaz(self, html, proxy):
        pass

    def testing_ipip(self, html, proxy):
        pass

    def testing_ipcn(self, html, proxy):
        pass

    def testing_ip138(self, html, proxy):
        pass

    def testing_tool_ip(self, html, proxy):
        pass

    def testing_sohu(self, html, proxy):
        pass

    def testing_online_service(self, html, proxy):
        pass


class NormalProxy(BaseProxy):

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

    def get_test_proxy(self, proxy=None):
        """
        测试代理是否成功
        :param proxy: 代理
        :return: 成功返回True,失败范围False
        """
        # url = 'http://httpbin.org/ip'
        url = 'https://www.ipip.net/ip.html'
        # 表示测试爬取的所有结果
        # 待测试的代理
        testing_proxy = []
        tested_proxy = []  # 已测试的代理
        for item in self.proxy_list:
            if 'qq代理' not in item.keys():
                testing_proxy.append(item)
            else:
                tested_proxy.append(item)
        tasks = []
        for proxy in testing_proxy:
            tasks.append(gevent.spawn(self.request_common_url, url, None, proxy))
        gevent.joinall(tasks)


class ThreadProxy(BaseProxy):

    def request_site(self, proxy_urls):
        """
        获取代理网站的源码数据,单个url的方式
        :return:
        """
        url = proxy_urls.get('url')
        url_name = proxy_urls.get('type')
        self.request_common_url(url, url_name, False)

    def get_test_proxy(self, proxy=None):
        """
        测试代理是否成功
        :param proxy: 代理
        :return: 成功返回True,失败范围False
        """
        # url = 'http://httpbin.org/ip'
        url = 'https://www.ipip.net/ip.html'

        testing_proxy = []  # 待测试的代理
        tested_proxy = []  # 已测试的代理
        for item in self.proxy_list:
            if 'qq代理' not in item.keys():
                testing_proxy.append(item)
            else:
                tested_proxy.append(item)

        self.request_common_url(url, None, proxy)


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
    print(len(res.proxy))
    proxy_list = res.proxy
    proxy_list = proxy_duplicate_removal(proxy_list)
    return proxy_list


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
