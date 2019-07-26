# IPproxy

* 利用Python以及各种库完成一个代理IP池


## 基本说明

* 本项目功能待更新，目前只完成了部分,建议先不要使用,还有些问题需要优化

* 抓取各大代理网站的免费代理，组成一个代理池，已自动附带UA(user-agent)代理池


## 计划待更新的功能：

* 部分待优化完善

* 将爬到的数据存入mysql数据库作永久存储，将代理的一部分存入redis作为中间层临时存储

* requests库爬取数据时，还是无法解决访问请求时的阻塞情况，后期考虑使用aiohttp代替reqeuests

* 对一些还未做解析的爬虫网站进行解析

* 后期考虑搭建一个服务器，访问服务器时返回json格式的代理ip，实时更新代理数据


## 开发环境

* Python3.7
* requests
* gevent
* lxml
* bs4
* json


* 安装必须的库

    ``pip install -r requirements.txt ``
    
## 文件说明：

* config.py
	+ 相关配置文件，里面主要是UA，代理网站链接，测试ip的网站，可以自己扩展，根据里面已有的数据格式添加即可
* headers.py
	+ 获取一个随机UA头，自动生成一个请求头
* proxy.py 
	+ 主要的逻辑代码
* proxy.txt
	+ 简单文件版存储，爬取到的可用代理


## 使用说明：

* 根据文字说明操作即可，分了三个方法，第一个是协程式，第二个是线程池，第三个是线程池+异步


## 运行：

* 直接运行proxy.py文件即可，config.py与headers.py请保证和proxy.py同在一目录下

* 爬取部分：
![爬取](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy.png)

* redis数据库结果：

![数据库获取](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy2.png)

## 自定制：

* 可以自己添加，自己重置UA，设置请求头
* 可以自己添加需要爬取的代理IP，config.py文件里有说明
* 自添加爬取的代理IP之后，需要自定制对应的方法，自己设置解析网站和测试代理IP的方法
* BaseProxy类可自定制，可自扩展方法
* 部分功能还不完善，会尽量做到方便后期更新迭代自定制

## 更多技能点：

### [我的博客](https://www.cnblogs.com/Eeyhan '博客')