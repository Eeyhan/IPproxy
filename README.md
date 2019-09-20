# IPproxy

* 利用Python的requests/re/beautifulsoup/tesseract等模块，完成的一个代理IP池，自动测试代理可用性，将数据持久化存储


## 基本说明

* 本项目已完成，可以使用，部分小功能待优化更新

* 抓取各大代理网站的免费代理，组成一个代理池，已自动附带UA(user-agent)代理池

* 程序流程图
	+ [程序流程](http://naotu.baidu.com/file/b754a429094727b85240df587d005a3c?token=fd57d469e8309269)

## 更新进度：

### 2019/7/30更新

* 破解66ip代理网站的加密字段，较之前能达到120个以上的可用代理


### 2019/7/29更新

* 增加更多的代理网站，以提高可用代理量

* 利用tessertact-ocr提取技术，把图片中的文字提取出来

## 计划待更新的功能：


* requests库爬取数据时，还是无法解决访问请求时的阻塞情况，后期考虑使用aiohttp代替reqeuests



## 开发环境

* Python3.7
* requests
* gevent
* lxml
* bs4
* json
* ThreadPoolExecutor
* flask
* pytesseract

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

* 因为爬取的代理网站众多，测试代理可用性也需要些时间，初次爬取代理时所耗时间平均在5-6分钟，后续取数据阶段则会很快

### 终端方式运行：

* 在运行之前自行安装配置redis数据库

* 在运行之前自行安装配置tesseract引擎

* 直接按proxy.py文件选择不同方法，取消相关的注释并运行proxy.py文件即可，config.py与headers.py请保证和proxy.py同在一目录下

### web方式运行：

* web方式运行调取的是从redis数据库中取出的数据，如果redis没有数据则先爬取数据再以web方式运行

* 启动main.py文件，用flask将结果以web页面的方式返回代理池，如果希望搭建在服务器上的话则可以此方式启动


#### 注：以web方式返回结果有点慢，因为为了保证返回的结果100%可用性，后台在自动测试代理可用性，如果对速度有要求，可以将相应的测试代码部分注释掉


## 运行结果：

### 数据库内无值时：

* 爬取部分：

![爬取](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy5.png)


* redis数据库结果：

![数据库获取](https://raw.githubusercontent.com/Eeyhan/pictures/master/redis.png)


### 数据库内有值时：

* 测试代理部分：

![测试代理](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy3.png)

* 将可用的重新再存入数据库：

![数据库内新的值](https://raw.githubusercontent.com/Eeyhan/pictures/master/proxy4.png)


### web方式启动结果：

![web页面启动](https://raw.githubusercontent.com/Eeyhan/pictures/master/flask.png)


## 自定制：

* 支持自己添加，自己重置UA，设置请求头

* 支持自己添加需要爬取的代理IP，config.py文件里有说明，自添加爬取的代理IP之后，需要自定制对应的方法，自己设置解析网站和测试代理IP的方法

* 支持NormalProxy类自定制，自扩展方法


## 更多技能点：

### [我的博客](https://www.cnblogs.com/Eeyhan '博客')