# IPproxy

## 说明

* 本项目功能待更新，目前只完成了部分,建议先不要使用

* 抓取各大代理网站的免费代理，组成一个代理池，已自动附带UA(user-agent)代理池

## 开发环境
* Python3.7
* requests
* gevent
* lxml
* bs4

* 安装必须的库
    ``pip install -r requirements.txt ``
    
## 文件说明：

* config.py文件为相关配置文件，里面主要是UA，代理网站链接，测试ip的网站，可以自己扩展，根据里面已有的数据格式添加即可
* headers.py是获取一个随机UA头，自动生成一个请求头
* proxy.py 是主要的逻辑代码

## 运行：（目前只完成了部分，可以获取结果，但是还未测试代理IP可用性）
* 根据文字说明操作即可

## 更多技能点：关注我的博客
* [技术博客](https://www.cnblogs.com/Eeyhan '技术博客')