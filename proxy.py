#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : proxy.py

import gevent
from gevent import monkey

monkey.patch_all()  # 如果是要开启进程池需要把这个注释掉
import json
import re
import asyncio
import requests
from lxml import etree
from bs4 import BeautifulSoup
import random
from functools import reduce
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, FIRST_COMPLETED
import time
import redis
import pytesseract
from PIL import Image
import os
import js2py
from config import PROXY_URLS, USER_AGENT, TEST_PROXY_URLS, POOL


class BaseProxy(object):
    """获取代理IP"""

    def __init__(self):
        self.header = None
        self.proxy_list = []  # 代理IP列表
        self.user_agent = USER_AGENT  # 请求的UA
        self.user_agent_66ip = random.choice(USER_AGENT)  # 66ip代理使用
        self.header = self.get_header  # 请求头

        # 节省创建对象的资源
        self.test_proxy_urls = self.get_test_site  # 测试代理IP的网址
        self.proxy_urls = self.get_proxy_site  # 免费代理网址

    def req_user_agent(self):
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
        return self.req_proxy_urls()

    def req_proxy_urls(self):
        """
        获取代理站点，重新拼接字段
        :return: 返回代理ip地址
        """
        proxy_url_list = []
        for item in PROXY_URLS:
            item['type'] = 'parser_' + item['type']
            proxy_url_list.append(item)
        self.proxy_urls = proxy_url_list
        return self.proxy_urls

    @property
    def get_test_site(self):
        """
        预留的钩子函数，返回的值可以由子类自定制
        :return:
        """

        return self.req_test_proxy_urls(TEST_PROXY_URLS)

    def req_test_proxy_urls(self, test_urls):
        """
        预留的钩子函数，返回的值可以由子类自定制
        :param test_urls: 测试代理IP的url
        :return:
        """
        test_proxy_urls = []
        for item in test_urls:
            item['type'] = 'test_' + item['type']
            test_proxy_urls.append(item)
        self.test_proxy_urls = test_proxy_urls
        return self.test_proxy_urls

    @property
    def get_header(self):
        """
        :return: 返回构造好的header头信息
        """
        user_agent = self.req_user_agent()
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': random.choice(user_agent),
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Accept-Encoding': 'gzip, deflate',
            'Upgrade-Insecure-Requests': '1'
        }
        return headers

    def request_common_url(self, url, url_name=None, proxy=None):
        """
        访问网站的通用方法
        :param url: 网站链接
        :param url_name: 请求代理网站时的别名，如果是测试代理不传入该值
        :param proxy: 代理参数
        :return:
        """
        html = None
        if proxy:  # 如果有代理
            headers = self.header
            headers['Referer'] = url
            headers['Connection'] = 'close'
            try:
                res = requests.get(url, headers=headers, proxies=proxy, timeout=(3, 7))
            except BaseException as x:
                # print('访问出错' % proxy)
                return
            if not res or res.status_code != 200:
                # print('该代理 %s 不可用' % proxy)
                return
        else:  # 不是测试代理
            try:
                if '66ip' in url:
                    headers = self.header
                    headers['User-Agent'] = self.user_agent_66ip
                    res = requests.get(url, headers=headers, timeout=(3, 7))
                else:
                    res = requests.get(url, headers=self.header, timeout=(3, 7))
            except Exception as e:
                # print(e)
                return
            if res.status_code != 200:
                # 如果是解析的66ip网站
                if url_name and url_name == 'parser_66ip':
                    res = self.solve_66ip(res)
                else:
                    # print('错误：网络请求超时，可能请求被拒绝')
                    pass
            if not res:
                # print('错误：网络请求超时，可能请求被拒绝')
                return
        if res:
            try:
                html = res.content.decode('utf-8')
            except Exception as s:
                # print(s)
                html = res.content.decode('gb2312')

        if url_name:
            if url_name.startswith('parser'):
                result = self.parser(html, url_name)
            elif url_name.startswith('test'):
                result = self.parser(html, url_name, proxy)
            return result

        elif not url_name:
            return res, html
        else:
            return

    def solve_66ip(self, response):
        """
        处理66ip的js加密
        :param response: 第一次请求返回的js数据
        :return: 返回解密好的网页数据
        """
        cookie = response.headers["Set-Cookie"]
        js = response.text.encode("utf8").decode("utf8")
        js = js.replace("<script>", "").replace("</script>", "").replace("{eval(", "{var data1 = (").replace(chr(0),
                                                                                                             chr(32))
        # 使用js2py处理js
        context = js2py.EvalJs()
        context.execute(js)
        js_temp = context.data1
        index1 = js_temp.find("document.")
        index2 = js_temp.find("};if((")
        js_temp = js_temp[index1:index2].replace("document.cookie", "data2")
        try:
            context.execute(js_temp)
        except Exception as e:
            # time.sleep(2)
            # context.execute(js_temp)
            pass
        data = context.data2

        # 合并cookie，重新请求网站。
        cookie += ";" + data
        response = requests.get("http://www.66ip.cn/mo.php?tqsl=1024", headers={
            "User-Agent": self.user_agent_66ip,
            "cookie": cookie,
        })
        return response

    def compare_proxy(self, proxy, current_ip):
        """
        拆分代理，只要ip:port
        :param proxy:爬取的代理ip
        :param current_ip: IP查询网站显示的ip
        :return:
        """

        proxy_ip = list(proxy.values())[0].split('//')[1]
        if current_ip in proxy_ip:  # current_ip:x.x.x.x proxy_ip:x.x.x.x:xx
            print(proxy)
            return True
        # print('current', current_ip, type(current_ip))
        # print('proxy', proxy_ip, type(proxy_ip))
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
            task.append(gevent.spawn(self.request_common_url, url, url_name, None))
        gevent.joinall(task)

    def request_test_site(self, test_urls=None):
        """
        预留的钩子函数，可以重新定义该方法，获取测试代理IP并测试
        :param test_urls:测试的urls
        :return:
        """
        tasks = []
        for item in self.proxy_list:
            tasks.append(gevent.spawn(self.choice_testsite_request, item))
        gevent.joinall(tasks)

    def parser(self, html, url_name, proxy=None):
        """
        测试代理的分发解析器
        :param html: 拿到的网站源码
        :param url_name: 请求的代理网站别名
        :param proxy: 待测试的代理ip,如果为空则是爬取阶段，如果不为空则是测试代理阶段
        :return:
        """
        func = getattr(self, url_name)
        # 如果对象存在对应解析方法
        if func:
            # 如果是goubanjia，用BeautifulSoup解析
            try:
                if url_name in ('parser_goubanjia', 'parser_66ip'):
                    html = BeautifulSoup(html, "lxml")
                    result = func(html)
                # 此类用字符串处理或者用正则匹配
                elif url_name in (
                        'test_sohu', 'test_onlineservice', 'test_ican', 'test_myip', 'test_httpbin', 'parser_github'):
                    # result = func(html, proxy)
                    if not proxy:
                        result = func(html)
                    else:
                        result = func(html, proxy)
                # 其余用xpath解析
                else:
                    html = etree.HTML(html)
                    if not proxy:
                        result = func(html)
                    else:
                        result = func(html, proxy)
            except Exception as e:
                # print(e)
                pass
            else:
                return result
        else:
            raise ValueError('尚不存在该网站的解析方法，请根据配置文件添加对应解析方法')

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
        # print(self.proxy_list)
        return self.proxy_list

    def decrypt_port(self, port_word):
        """
        解密被加密的真实端口号，该字段放在标签的属性里
        :param port_word: 加密字段
        :return:
        """
        word = list(port_word)
        num_list = []
        for item in word:
            num = 'ABCDEFGHIZ'.find(item)
            num_list.append(str(num))
        port = int("".join(num_list)) >> 0x3
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
                            port = self.decrypt_port(class_list[1])
                            # 拼接端口
                            text = text + ":" + str(port)
                    else:
                        if child.string != None:
                            text = text + child.string
                temp_list.append(text)
        data = zip(prototal_list, temp_list)
        for item in data:
            self.proxy_list.append({item[0]: item[0] + '://' + item[1]})
        # print(proxy_list)
        return self.proxy_list

    def parser_da5u(self, html):
        """
        da5u代理解析
        :param html:
        :return:
        """

        ports = html.xpath('//li[contains(@class,"port")]')
        port_list = []
        for port in ports:
            encryption_port = port.values()[0].split(' ')[1]
            port = self.decrypt_port(encryption_port)
            port_list.append(port)

        items = html.xpath('//ul[@class="l2"]')
        temp_data = []
        for item in items:
            xpath_data = item.xpath('./span/li/text()')
            ip = xpath_data[0]
            protocal = xpath_data[3]
            temp_data.append([ip, protocal])

        res = zip(temp_data, port_list)
        for item in res:
            proxy = {item[0][1]: item[0][1] + '://' + item[0][0] + ':' + str(item[1])}
            self.proxy_list.append(proxy)
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
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_mipu(self, html):
        """
        米扑代理解析 该方法未完善，后续补充
        :param html: etree对象
        :return:
        """
        response_ip = html.xpath('//td[@class="tbl-proxy-ip"]')
        response_protocal = html.xpath('//td[@class="tbl-proxy-type"]')
        ips = []
        protocals = []
        for item in response_ip:
            xpath_data = item.xpath('string(.)')
            ips.append(xpath_data)
        for item in response_protocal:
            xpath_data = item.xpath('string(.)').lower()
            temp_protocal = 'https' if 'https' in xpath_data else 'http'
            protocals.append(temp_protocal)

        # 这里考虑再三，不能用并发提速，因为并发会乱序，导致ip和端口无法对应

        response_port = html.xpath('//td[@class="tbl-proxy-port"]')
        url_start = 'https://proxy.mimvp.com/'
        ports = []
        for item in response_port:
            port_img = url_start + item.xpath('./img/@src')[0]
            headers = self.header
            data = requests.get(port_img, headers=headers).content
            port = self.ocr_get_port(data)
            ports.append(port)

        result = zip(protocals, ips, ports)
        for item in result:
            self.proxy_list.append({item[0]: item[0] + '://' + item[1] + ':' + item[2]})

        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def ocr_get_port(self, data):
        """
        用ocr提取图片中的端口
        :param data: 返回的图片二进制流结果
        :return:
        """

        f = open('port.png', 'wb')
        f.write(data)
        f.close()

        pytesseract.pytesseract.tesseract_cmd = 'C://Program Files//Tesseract-OCR//tesseract.exe'
        port = pytesseract.image_to_string(Image.open('port.png'),
                                           config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')

        # 删除图片
        os.remove('port.png')

        return port

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
        # print(self.proxy_list, len(self.proxy_list))
        return self.proxy_list

    def parser_github(self, html):
        """
        解析github上的数据
        :param html:
        :return:
        """
        proxies = html.split('\n')
        for item in proxies:
            res = json.loads(item)
            port = res.get('port')
            ip = res.get('host')
            protocal = res.get('type')
            proxy = {protocal: protocal + '://' + ip + ':' + str(port)}
            self.proxy_list.append(proxy)

    def parser_xsdaili(self, html):
        """
        小舒代理网站解析
        :param html:
        :return:
        """
        # 爬取每天的最新的
        res = html.xpath('//div[contains(@class,"ips")][position()<3]')
        url_start = 'http://www.xsdaili.com'

        for item in res:
            second_url = url_start + item.xpath('./div[@class="title"]/a/@href')[0]
            result = self.get_xsdaili_result(second_url)
            self.proxy_list.append(result)

        return self.proxy_list

    def get_xsdaili_result(self, url):
        """
        小舒代理二层网页爬取
        :param url:
        :return:
        """
        headers = self.header
        response = requests.get(url, headers=headers).content
        try:
            content = response.decode('utf-8')
        except Exception as e:
            # print(e)
            content = response.decode('gb2312')
        etree_html = etree.HTML(content)
        items = etree_html.xpath('//div[@class="cont"]/text()')[:-1]
        proxies = []
        for item in items:
            ip_port, protocal = item.strip().split('@')
            protocal = protocal.split('#')[0].lower()
            proxy = {protocal: protocal + '://' + ip_port}
            proxies.append(proxy)
        return proxies

    def parser_66ip(self, html):
        """
        解析66ip的代理
        :param html: beautifulsoup对象
        :return:
        """
        res = html.find('p').stripped_strings
        for item in res:
            if '$' in item or '}' in item:
                continue
            self.proxy_list.append({'http': 'http://' + item})
        return self.proxy_list

    def choice_testsite_request(self, proxy):
        """
        选择测试网站并测试代理是否可用
        :param proxy: 待测试的代理
        :return:
        """
        test_url = random.choice(self.test_proxy_urls)
        url = test_url.get('url')
        url_name = test_url.get('type')
        result = self.request_common_url(url, url_name, proxy)
        if not result:
            self.proxy_list.remove(proxy)
        return self.proxy_list

    def get_test_proxy(self, proxy=None):
        """
        测试代理是否成功
        :param proxy: 代理，如果为None则为协程使用，如果不为None则为线程使用
        :return: 成功返回True,失败范围False
        """

        if not proxy:
            self.request_test_site()
        else:
            result = self.choice_testsite_request(proxy)
            if result:
                return result
            else:  # 如果没有结果，换个测试网站重新测试
                pass
            # # 递归查找，直到有正常数据返回
            # self.get_test_proxy(proxy)

    @property
    def proxy(self):
        """测试代理入口方法"""
        self.get_test_proxy()
        return self.proxy_list

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
    def proxies(self):
        """
        入口方法，返回代理IP数组
        :return:
        """
        result = self.get_proxy()
        return result

    def test_baidu(self, etree_html, proxy):
        """
        用代理ip测试访问百度网站
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """
        current_ip = etree_html.xpath('//span[@class="c-gap-right"]/text()')[0].split(':')[1].strip()
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)

        if result:
            return proxy

    def test_sogou(self, etree_html, proxy):
        """
        用代理ip测试访问搜狗网站
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//div[@id="ipsearchresult"]/strong/text()')[0].split('   ')[0].strip()
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_so(self, etree_html, proxy):
        """
        用代理ip测试访问360搜索网站
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//p[@class="mh-detail "]/span/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_miji(self, etree_html, proxy):
        """
        用代理ip测试访问秘迹网站
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//*[@id="main_results"]/div[2]/span/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)

        if result:
            return proxy

    def test_chinaz(self, etree_html, proxy):
        """
        chinaz的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//*[@id="rightinfo"]/dl/dd[1]/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)

        if result:
            return proxy

    def test_ipip(self, etree_html, proxy):
        """
        ipip的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//input/@value')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_ipcn(self, etree_html, proxy):
        """
        ipcn的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//div[@id="result"]/div/p[1]/code/text()')
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_luip(self, etree_html, proxy):
        """
        luip的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//*[@id="ipaddress"]/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)

        if result:
            return proxy

    def test_ttt(self, etree_html, proxy):
        """
        ttt的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//*[@id="getip"]/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_taobao(self, etree_html, proxy):
        """
        ttt的IP查询
        :param etree_html: etree对象
        :param proxy: 待测试的代理IP
        :return:
        """

        current_ip = etree_html.xpath('//*[@id="obviousIp"]/text()')[0]
        current_ip = str(current_ip)
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

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

    def test_ican(self, html, proxy):
        """
        ican的IP查询
        :param html: 源网站页面,返回的就是ip地址
        :param proxy: 待测试的代理IP
        :return:
        """
        result = self.compare_proxy(proxy, html)
        if result:
            return proxy

    def test_myip(self, html, proxy):
        """
        myip的IP查询
        :param html: 源网站页面
        :param proxy: 待测试的代理IP
        :return:
        """
        # html = html.replace(' ', '').split('：')[1].split('来')[0]
        current_ip = re.findall(r'\d+\.\d+\.\d+\.\d+', html)[0]
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy

    def test_httpbin(self, html, proxy):
        """
        httpbin的IP查询
        :param html: 源网站页面,返回的是json字符串
        :param proxy: 待测试的代理IP
        :return:
        """
        html = json.loads(html)
        current_ip = html.get('origin')
        result = self.compare_proxy(proxy, current_ip)
        if result:
            return proxy


class NormalProxy(BaseProxy):
    """通用类，如果要扩展功能，可以在此扩展"""
    pass


class ThreadProxy(BaseProxy):
    """线程式的类，方便线程调用"""

    def request_site(self, proxy_urls):
        """
        获取代理网站的源码数据,单个url的方式
        :return:
        """
        url = proxy_urls.get('url')
        url_name = proxy_urls.get('type')
        self.request_common_url(url, url_name, None)


def proxy_duplicate_removal(lists):
    """
    对爬取到的数据去重
    :return:
    """
    proxy_list = lambda x, y: x if y in x else x + [y]
    return reduce(proxy_list, [[], ] + lists)


def save_redis(proxy_list, key=None):
    """
    存储到redis
    :param proxy_list: 代理列表
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    if not key:
        key = 'proxies'

    # 检测是否已有值
    cont = conn.get(key)
    if cont:
        cont = eval(cont)
        proxy_list.extend(cont)
    conn.set(key, str(proxy_list))


def get_redis(key=None):
    """
    从redis获取值
    :param key: redis的key
    :return:
    """
    conn = redis.Redis(connection_pool=POOL)
    if not key:
        key = 'proxies'
    proxies = conn.get(key)
    if proxies:
        proxies = eval(proxies)
    proxy_list = db_test_proxy(proxies)
    print('数据库内还有 %s 个代理可用' % len(proxy_list))
    return proxy_list


def thread_exector(thread, res):
    """
    线程池启动
    :param thread: 线程池对象
    :param res: 自定义ThreadProxy对象
    :return:
    """
    tasks = [thread.submit(res.get_test_proxy, proxy) for proxy in res.proxy_list]
    thread.shutdown()
    wait(tasks, return_when=FIRST_COMPLETED)
    # thread2.shutdown()
    result = [obj for obj in as_completed(tasks)]
    return result


def thread_exector_asynic(thread, res):
    """
    线程池异步方法启动
    :param thread: 线程池对象
    :param res: 自定义ThreadProxy对象
    :return:
    """
    loop = asyncio.get_event_loop()
    tasks = [loop.run_in_executor(thread, res.get_test_proxy, url) for url in res.proxy_list]
    loop.run_until_complete(asyncio.wait(tasks))
    return tasks


def db_test_proxy(proxies):
    # 测试代理ip
    res = ThreadProxy()
    res.proxy_list = proxies

    print('开始测试数据库内代理IP可用性.........')
    thread = ThreadPoolExecutor()
    proxy_list = []

    # ################ 以下两个不能共用 ############

    # 说明：如果直接运行proxy.py文件，则推荐使用线程池+异步的方式，如果是flask调用，则推荐线程池的方式

    # 线程池方式
    tasks = thread_exector(thread, res)

    # # 线程池+异步的方式
    # tasks = thread_exector_asynic(thread, res)

    for item in tasks:
        temp_res = item.result()
        if temp_res:
            proxy_list.extend(temp_res)

    proxy_list = proxy_duplicate_removal(proxy_list)
    print('一共有%s个可用的代理' % len(proxy_list))
    save_redis(proxy_list)
    return proxy_list


def main_gevent():
    # 利用协程记得monkey打补丁

    # 爬取部分
    res = NormalProxy()
    proxy_list = res.proxies
    # print(proxy_list, len(res.proxies))

    # 测试代理部分
    print('开始测试代理IP可用性.........')
    available_proxy_list = res.proxy
    save_redis(available_proxy_list)
    return available_proxy_list


def main_thread_pool():
    # 利用线程池要比协程速度快

    # 爬取部分
    res = ThreadProxy()
    thread = ThreadPoolExecutor()
    tasks1 = [thread.submit(res.get_proxy, url) for url in PROXY_URLS]
    thread.shutdown()
    temp_data = [obj.result() for obj in as_completed(tasks1)]
    data = []
    for item in temp_data:
        data.extend(item)
    proxy_list = proxy_duplicate_removal(data)

    # 测试代理部分
    print('开始测试代理IP可用性.........')
    res.proxy_list = proxy_list
    thread2 = ThreadPoolExecutor()
    tasks2 = [thread2.submit(res.get_test_proxy, proxy) for proxy in res.proxy_list]
    wait(tasks2, return_when=FIRST_COMPLETED)
    # thread2.shutdown()
    temp_data2 = [obj for obj in as_completed(tasks2)]
    data2 = []
    for item in temp_data2:
        temp_res = item.result()
        if temp_res:
            data2.extend(temp_res)
    data2 = proxy_duplicate_removal(data2)

    # 存储到redis
    print('一共爬取了%s个可用的代理' % len(proxy_list))
    save_redis(data2)
    return data2


# def main_process_pool():
#     # 此处利用进程不讨巧
#     res = ThreadProxy()
#     tasks = []
#     process = ProcessPoolExecutor(max_workers=3)
#     for url in PROXY_URLS:
#         obj = process.submit(res.get_proxy, url).result()
#         tasks.append(obj)
#     process.shutdown()
#     proxy_list = [obj.result() for obj in tasks]
#     print(len(proxy_list))
#     return proxy_list


def main_thread_pool_asynicio():
    # 线程池+异步

    # 爬取部分
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

    # 测试代理部分
    print('开始测试代理IP可用性.........')
    res.proxy_list = proxy_list
    loop2 = asyncio.get_event_loop()
    thread2 = ThreadPoolExecutor()
    tasks2 = [loop2.run_in_executor(thread2, res.get_test_proxy, url) for url in res.proxy_list]
    loop2.run_until_complete(asyncio.wait(tasks2))

    proxy_list2 = []
    for item in tasks2:
        temp_res = item.result()
        if temp_res:
            proxy_list2.extend(temp_res)
    proxy_list2 = proxy_duplicate_removal(proxy_list2)

    # 存储到redis
    print('一共爬取了%s个可用的代理' % len(proxy_list))
    save_redis(proxy_list2)

    return proxy_list2


if __name__ == '__main__':
    # ############### 数据库为空时 ###############
    """以下根据自己的使用需求取消注释运行，注意：千万不能三个方法同时运行，会导致数据紊乱"""
    start = time.time()
    # 第一种，使用协程，速度稍微慢些，但是占用资源小
    # main_gevent()

    # 第二种，使用线程池，速度最快
    # res = main_thread_pool()

    # 第三种，使用线程池+异步io，综合性更强，推荐该方法
    res2 = main_thread_pool_asynicio()
    print('总用时:', time.time() - start)

    """数据库有值和数据库无值时不能混合使用，容易导致数据紊乱，且当数据库无值存储时已做过代理验证"""
    # ############### 数据库有值时 ###############

    # res = get_redis()
    # print(res)
