# IPproxy

* 利用Python以及各种库完成一个代理IP池，自动测试代理可用性，将数据持久化存储


## 基本说明

* 本项目功能待更新，目前只完成了部分,建议先不要使用,还有些问题需要优化

* 抓取各大代理网站的免费代理，组成一个代理池，已自动附带UA(user-agent)代理池


## 计划待更新的功能：

* 部分待优化完善

* requests库爬取数据时，还是无法解决访问请求时的阻塞情况，后期考虑使用aiohttp代替reqeuests

* 对一些还未做解析的爬虫网站进行解析


## 开发环境

* Python3.7
* requests
* gevent
* lxml
* bs4
* json
* ThreadPoolExecutor
* flask


* 安装必须的库

    ``pip install -r requirements.txt ``
    
## 相关说明：

* config.py
	+ 相关配置文件，里面主要是UA，代理网站链接，测试ip的网站，可以自己扩展，根据里面已有的数据格式添加即可
* headers.py
	+ 获取一个随机UA头，自动生成一个请求头
* proxy.py 
	+ 主要的逻辑代码
* main.py
    + 以flask作为web服务启动文件

* 根据文字说明操作即可，分了三个方法，第一个是协程式，第二个是线程池，第三个是线程池+异步，自行选择

* 从数据库调取数据部分，分了两个方法测试代理可用性，第一个是线程池方法，第二个是线程池+异步方法，自行选择

## 运行：

### 终端方式运行：

* 在运行之前自行安装配置redis数据库

* 直接按proxy.py文件选择不同方法，取消注释运行proxy.py文件即可，config.py与headers.py请保证和proxy.py同在一目录下

### web方式运行：

* 启动main.py文件，用flask将结果以web页面的方式返回代理池，如果希望搭建在服务器上的话则可以此方式启动


![web页面启动](https://raw.githubusercontent.com/Eeyhan/pictures/master/flask.png)

#### 注：以web方式返回结果有点慢，因为为了保证返回的结果100%可用性，后台在自动测试代理可用性，如果对速度有要求，可以将相应的测试代码部分注释掉


### 数据库内无值时：

* 爬取部分：

![爬取](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy.png)

* redis数据库结果：

![数据库获取](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy2.png)


### 数据库内有值时：

* 测试代理部分：

![测试代理](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy3.png)

* 将可用的重新再存入数据库：

![数据库内新的值](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy4.png)


## 自定制：

* 支持自己添加，自己重置UA，设置请求头

* 支持自己添加需要爬取的代理IP，config.py文件里有说明，自添加爬取的代理IP之后，需要自定制对应的方法，自己设置解析网站和测试代理IP的方法

* 支持BaseProxy类自定制，自扩展方法


## 更多技能点：

### [我的博客](https://www.cnblogs.com/Eeyhan '博客')