#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author  : geek_yang
# @File    : main.py

from flask import Flask
from proxy import get_redis

app = Flask(__name__)


@app.route('/')
def index():
    """
    主视图函数
    :return:
    """
    # 取redis数据库内的数据
    data = get_redis()
    res = ''
    for item in data:
        res += '<p>' + str(list(item.values())[0]) + '</p>'

    return res


if __name__ == '__main__':
    app.run()
