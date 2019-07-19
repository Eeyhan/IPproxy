#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : geek_yang
# @File    : v2.py

import requests
import urllib.parse
import random
from headers import get_headers


def choice_browser_header():
    headers = get_headers()
    print(headers)
    return headers


def kanzhun(args):
    """
    看准网爬取
    :param args:搜索关键词
    :return:
    """
    args = urllib.parse.quote(args)
    url = 'https://www.kanzhun.com/jobl/p/?stype=&q=%s' % args
    headers = choice_browser_header()
    res = requests.get(url, headers=headers)
    # print(res.status_code)
    print(res.content.decode('utf-8'))


kanzhun('python')
