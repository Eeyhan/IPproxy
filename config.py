#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : Eeyhan
# @File    : config.py


import redis

"""
自添加USER_AGENT请按照已有数据的格式来添加
"""

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
    'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Tri dent/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)',
    'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64;Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)',
]

"""
自添加PROXY_URLS请按照已有数据的格式来添加
"""

PROXY_URLS = [
    {'url': 'https://www.xicidaili.com/nn', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/nt', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/wn', 'type': 'xici'},
    {'url': 'https://www.xicidaili.com/wt', 'type': 'xici'},
    {'url': 'http://www.xiladaili.com/gaoni/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/http/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/https/', 'type': 'xila'},
    {'url': 'http://www.xiladaili.com/putong/', 'type': 'xila'},
    {'url': 'https://www.kuaidaili.com/free/intr/', 'type': 'kuaidaili'},
    {'url': 'https://www.kuaidaili.com/free/inha/', 'type': 'kuaidaili'},
    {'url': 'https://www.kuaidaili.com/ops/', 'type': 'kuaidaili_new'},
    {'url': 'http://www.89ip.cn/', 'type': '89ip'},
    {'url': 'http://www.qydaili.com/free/', 'type': 'qydaili'},
    {'url': 'https://ip.ihuan.me/', 'type': 'ihuan'},
    {'url': 'http://www.ip3366.net/', 'type': '3366'},
    {'url': 'http://www.iphai.com/free/ng', 'type': 'iphai'},
    {'url': 'http://www.iphai.com/free/wg', 'type': 'iphai'},
    {'url': 'http://www.iphai.com/free/wp', 'type': 'iphai'},
    {'url': 'http://www.goubanjia.com/', 'type': 'goubanjia'},
    {'url': 'http://www.feiyiproxy.com/?page_id=1457', 'type': 'feiyi'},
    {'url': 'http://www.shenjidaili.com/open/', 'type': 'shenji'},
    {'url': 'http://ip.kxdaili.com/dailiip.html', 'type': 'kaixin'},
    {'url': 'http://www.superfastip.com/welcome/freeIP', 'type': 'jisu'},
    {'url': 'http://ip.jiangxianli.com/', 'type': 'jxl'},
    {'url': 'https://lab.crossincode.com/proxy/', 'type': 'cross'},
    {'url': 'http://www.nimadaili.com/gaoni/', 'type': 'nima'},
    {'url': 'http://www.nimadaili.com/http/', 'type': 'nima'},
    {'url': 'http://www.nimadaili.com/https/', 'type': 'nima'},
    {'url': 'http://www.data5u.com/', 'type': 'da5u'},
    {'url': 'https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list', 'type': 'github'},
    {'url': 'https://proxy.mimvp.com/freeopen.php', 'type': 'mipu'},  # 需要图片识别端口，已解决
    {'url': 'http://www.xsdaili.com/', 'type': 'xsdaili'},  # 需要爬取二级网页，已解决
    {'url': 'http://www.66ip.cn/mo.php?tqsl=1024', 'type': '66ip'},  # 需要js解密，已解决


]

"""
自添加测试代理的url请按照已有数据的格式来添加
"""

TEST_PROXY_URLS = [

    # 下面的是主流搜索引擎搜ip的网址，相对比较开放，而且查询结果比较准确
    {'url': 'https://www.baidu.com/s?wd=ip', 'type': 'baidu'},
    {'url': 'https://www.sogou.com/web?query=ip', 'type': 'sogou'},
    {'url': 'https://www.so.com/s?q=ip&src=srp&fr=none&psid=2d511001ad6e91af893e0d7e561f1bba', 'type': 'so'},
    {'url': 'https://mijisou.com/?q=ip&category_general=on&time_range=&language=zh-CN&pageno=1', 'type': 'miji'},

    # 下面的是专门查询本机公网ip的网址，请求不能过于频繁
    {'url': 'http://pv.sohu.com/cityjson', 'type': 'sohu'},
    {'url': 'http://ip.taobao.com/ipSearch.html', 'type': 'taobao'},
    {'url': 'https://myip.ipip.net/', 'type': 'myip'},
    {'url': 'http://httpbin.org/ip', 'type': 'httpbin'},
    {'url': 'http://ip.chinaz.com/', 'type': 'chinaz'},
    {'url': 'https://www.ipip.net/ip.html', 'type': 'ipip'},
    {'url': 'https://ip.cn/', 'type': 'ipcn'},
    {'url': 'https://tool.lu/ip/', 'type': 'luip'},
    {'url': 'http://api.online-service.vip/ip/me', 'type': 'onlineservice'},
    {'url': 'https://ip.ttt.sh/', 'type': 'ttt'},
    # {'url': 'http://icanhazip.com/', 'type': 'ican'},  # 该网站有时会返回一个ipv6地址，导致结果有误
]

# redis数据库连接池
POOL = redis.ConnectionPool(host='127.0.0.1', max_connections=5, decode_responses=True, db=1)
