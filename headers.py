#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : geek_yang
# @File    : my_headers.py

import random
from config import USER_AGENT


def get_headers():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'User-Agent': random.choice(USER_AGENT),
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
    }
    return headers
