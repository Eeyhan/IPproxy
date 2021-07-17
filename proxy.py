#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : proxy.py

import asyncio
import aiohttp
from settings import *
from copy import deepcopy
import random
from urllib.parse import urlparse, unquote
import re
from lxml import etree
import base64
import json
import aioredis
from bs4 import BeautifulSoup
import httpx


class AsyncMyRedis():
    _redis = None

    def __init__(self):
        pass

    async def get_redis_pool(self, *args, **kwargs):
        if not self._redis:
            self._redis = await aioredis.create_redis_pool(*args, **kwargs)
        return self._redis

    async def close(self):
        if self._redis:
            self._redis.close()
            await self._redis.wait_closed()


class FreeProxy():
    def __init__(self, page=5):
        self.page_begin = page
        self.temp_proxies = set()
        self.proxies = set()
        self.headers = HEADERS
        self.user_agent = USER_AGENT
        self.redis_client = None
        self.target = self.generate_target_urls

    async def get_redis_client(self):
        _redis = AsyncMyRedis()
        redis_client = await _redis.get_redis_pool((REDIS_HOST, REDIS_PORT), db=REDIS_DB,
                                                   encoding='utf-8')
        self.redis_client = redis_client

    @property
    def generate_target_urls(self):
        temp = deepcopy(TARGET)
        target = set()
        for item in temp:
            if 'page' in item:
                for i in range(self.page_begin):
                    if 'offset' in item:
                        offset = i * 50
                        url = item.format(page=i, offset=offset)
                    else:
                        url = item.format(page=i)
            else:
                url = item
            if url and '{page}' not in url:
                target.add(url)
        if target:
            return target

    async def fetch_urls(self):
        tasks = []
        async  with aiohttp.ClientSession() as client:
            for url in self.target:
                req = self.fetch(client, url)
                task = asyncio.create_task(req)
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def fetch(self, client, url, *args, **kwargs):
        print(12312312, url)
        resp,httpx_resp = None,None
        domain = urlparse(url).netloc
        ua = random.choice(self.user_agent)
        headers = deepcopy(self.headers)
        headers['user-agent'] = ua
        try:
            resp = await client.get(url, headers=headers, ssl=False, timeout=250)
        except (Exception, BaseException) as e:
            if resp:
                resp.close()
                await resp.wait_for_close()
            # print(12312312, e)
            await asyncio.sleep(round(random.uniform(0, 5)), 2)
            try:
                ua = random.choice(self.user_agent)
                headers = deepcopy(self.headers)
                headers['user-agent'] = ua
                resp = await client.get(url, headers=headers, ssl=False, timeout=250)
            except (Exception, BaseException) as e:
                print(44444444, e,url)
                if resp:
                    resp.close()
                    await resp.wait_for_close()
                    return
        if resp:
            status = resp.status
            if status == 200 or str(status).startswith('3'):
                try:
                    html = await resp.text(encoding='utf-8')
                except (Exception, BaseException) as e:
                    try:
                        html = await resp.text(encoding='gb18030')
                    except (Exception, BaseException) as e:
                        print('异常编码',e)
                        return
                if html:
                    flag = TARGET_DICT.get(domain)
                    resp.close()
                    if flag:
                        if hasattr(self, f'parser_{flag}'):
                            func = getattr(self, f'parser_{flag}')
                            await func(html)
            resp.close()


    async def base64_to_ip(str):
        s = base64.b64decode(str)
        if s:
            s = s.decode('utf-8')
            if s:
                return s

    async def parser_www_duplichecker_com(self, res):
        temp = re.findall(r'''\d+\.\d+\.\d+\.\d+\:\d+''', res, re.S | re.I)
        temp = [i.strip() for i in temp if i]
        if temp:
            print(f'已拿到网站 duplichecker_com 的{len(temp)}条代理')
            self.proxies.update(set(temp))

    async def parser_free_proxy_cz(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@id="proxy_list"]/tbody/tr')
        end = []
        for item in data:
            proxy = item.xpath('./td[@class="left"]/script/text()')
            proxy = ''.join(proxy).strip() if proxy else ''
            if proxy:
                proxy = proxy.replace('document.write(Base64.decode("', '').replace('"))', '')
                proxy = await self.base64_to_ip(proxy)
                if proxy:
                    end.append(proxy)
        if end:
            print(f'已拿到网站 free_proxy_cz 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_free_proxy_list_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@class="table table-striped proxy-list"]/tbody//tr')
        end = []
        for item in data:
            proxy = item.xpath('./td[1]/a/@title')
            proxy = ''.join(proxy) if proxy else ''
            end.append(proxy)
        if end:
            print(f'已拿到网站 free_proxy_list_com 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_www_idcloak_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@id="sort"]/tr[position()>1]')
        end = []
        for item in data:
            ip = item.xpath('./td[last()]/text()')
            ip = ''.join(ip) if ip else ''
            port = item.xpath('./td[last()-1]/text()')
            port = ''.join(port) if port else ''
            proxies = ip + ':' + port
            if proxies:
                end.append(proxies)
        if end:
            print(f'已拿到网站 www_idcloak_com 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_list_proxylistplus_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@class="bg"]/tr[position()>2]')
        end = []
        for item in data:
            ip = item.xpath('./td[2]/text()')
            port = item.xpath('./td[3]/text()')
            ip = ''.join(ip) if ip else ''
            port = ''.join(port) if port else ''
            if ip and port:
                proxy = ip + ':' + port
                end.append(proxy)
        if end:
            print(f'已拿到网站 list_proxylistplus_com 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_www_my_proxy_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//div[@class="list"]//text()')
        data = [i.split('#')[0] for i in data if i]
        if data:
            print(f'已拿到网站 www_my_proxy_com 的{len(data)}条代理')
            self.proxies.update(set(data))

    async def parser_proxy_list_org(self, res):
        html = etree.HTML(res)
        data = html.xpath('//div[@class="table-wrap"]/div//ul')
        end = []
        for item in data:
            proxy = item.xpath('./li[@class="proxy"]/script/text()')
            proxy = ''.join(proxy) if proxy else ''
            if proxy and 'Proxy' in proxy:
                proxy = proxy.replace('Proxy', '').replace('(', '').replace(')', '')
                proxy = await self.base64_to_ip(proxy)
                end.append(proxy)
        if end:
            print(f'已拿到网站 proxy_list_org 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_proxydb_net(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@class="table table-sm table-hover"]/tbody/tr')
        end = []
        for item in data:
            proxy = item.xpath('./td[1]/a/@href')
            proxy = ''.join(proxy) if proxy else ''
            proxy, protocal = proxy[1:].replace('/', ':').split('#')
            end.append(proxy)
        if end:
            print(f'已拿到网站 proxydb_net 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_www_proxynova_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//table[@id="tbl_proxy_list"]/tbody/tr')
        end = []
        for item in data:
            ip = item.xpath('./td[1]/abbr/script/text()')
            ip = ''.join(ip).strip() if ip else ''
            if ip:
                ip = ip.replace('document.write(', '').replace(');', '').replace("'", '')
            port = item.xpath('./td[2]/text()')
            port = ''.join(port).strip() if port else ''
            if ip and port:
                proxy = ip + ':' + port
                end.append(proxy)
        end = [i for i in end if i]
        if end:
            print(f'已拿到网站 www_proxynova_com 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_www_proxyrack_com(self, res):
        try:
            res = json.loads(res)
        except json.JSONDecodeError:
            return
        data = res.get('records')
        end = []
        for item in data:
            ip = item.get('ip')
            port = item.get('port')
            protocol = item.get('protocol')
            proxies = ip + ':' + port
            if proxies:
                end.append(proxies)
        if end:
            print(f'已拿到网站 www_proxyrack_com 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_www_proxyscan_io(self, res):
        html = etree.HTML(res)
        data = html.xpath('//tr')
        end = []
        for item in data:
            ip = item.xpath('./th/text()')
            port = item.xpath('./td[1]/text()')
            ip = ''.join(ip).strip() if ip else ''
            port = ''.join(port).strip() if port else ''
            if ip and port:
                proxy = ip + ':' + port
                end.append(proxy)
        if end:
            print(f'已拿到网站 www_proxyscan_io 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def parser_api_proxyscrape_com(self, res):
        res = BeautifulSoup(res, 'html.parser')
        data = res.select('table[class="proxies-table"]')
        if data:
            data = data[0]
            end = []
            for item in data.children:
                if item != '\n':
                    temp = item.select('td')
                    if temp:
                        ip = temp[0]
                        port = temp[1]
                        if ip and port:
                            proxy = ip.text + ':' + port.text
                            end.append(proxy)
            if end:
                print(f'已拿到网站 api_proxyscrape_com 的{len(end)}条代理')
                self.proxies.update(set(end))

    async def parser_smallseotools_com(self, res):
        html = etree.HTML(res)
        data = html.xpath('//div[@id="page-url-list"]/text()')
        data = [i.strip() for i in data if i]
        if data:
            print(f'已拿到网站 smallseotools_com 的{len(data)}条代理')
            self.proxies.update(set(data))

    async def parser_www_sslproxies_org(self, res):
        temp = re.findall(r'''\d+\.\d+\.\d+\.\d+\:\d+''', res, re.S | re.I)
        temp = [i.strip() for i in temp if i]
        if temp:
            print(f'已拿到网站 www_sslproxies_org 的{len(temp)}条代理')
            self.proxies.update(set(temp))

    async def parser_www_socks_proxy_net(self, res):
        temp = re.findall(r'''\d+\.\d+\.\d+\.\d+\:\d+''', res, re.S | re.I)
        temp = [i.strip() for i in temp if i]
        if temp:
            print(f'已拿到网站 www_socks_proxy_net 的{len(temp)}条代理')
            self.proxies.update(set(temp))

    async def parser_www_proxy_list_download(self, res):
        html = etree.HTML(res)
        data = html.xpath('//tbody[@id="tabli"]/tr')
        end = []
        for item in data:
            ip = item.xpath('./td[1]/text()')
            port = item.xpath('./td[2]/text()')
            ip = ''.join(ip) if ip else ''
            port = ''.join(port) if port else ''
            if ip and port:
                proxy = ip + ':' + port
                end.append(proxy)
        if end:
            print(f'已拿到网站 www_proxy_list_download 的{len(end)}条代理')
            self.proxies.update(set(end))

    async def save_redis(self, key=PROXY_KEY):
        if self.proxies:
            print(f'当前已存储代理 {len(self.proxies)} 个,正在存储')
            for item in self.proxies:
                await self.redis_client.sadd(key, item)
            print('已存储！！！')
            self.redis_client.close()

    async def get_proxies(self, key=PROXY_KEY):
        proxies = self.redis_client.smembers(key)
        if proxies:
            return proxies

    async def run(self):
        await self.get_redis_client()
        await self.fetch_urls()
        if self.proxies:
            await self.save_redis()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    proxy_obj = FreeProxy()
    loop.run_until_complete(proxy_obj.run())
