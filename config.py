# -*- coding:utf-8 -*-
import redis

HEADERS = {
    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'Connection': 'close',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
}

USER_AGENT = [
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Tri dent/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)',
    'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64;Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)'
]

TARGET = {
    'https://www.duplichecker.com/free-proxy-list.php',
    'http://free-proxy.cz/en/',
    'https://free-proxy-list.com/?page={page}port=&up_time=0',
    'http://www.idcloak.com/proxylist/proxy-list.html',  # -- r
    'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1',
    'https://www.my-proxy.com/free-proxy-list.html',  # -- r
    'https://proxy-list.org/english/index.php?p={page}', # -- r
    'http://proxydb.net/',
    'https://www.proxynova.com/proxy-server-list', # -- r
    # 'https://www.proxyrack.com/proxyfinder/proxies.json?page={page}&perPage=50&offset={offset}', # -- r
    'https://www.proxyrack.com/proxyfinder/proxies.json?page=',
    'https://www.proxyscan.io/home/filterresult?limit=100&page={page}&&status=',
    'https://api.proxyscrape.com/proxytable.php', #
    'https://scrapingant.com/free-proxies/', # --r
    'https://smallseotools.com/free-proxy-list/', # -- r
    'https://www.sslproxies.org/', # -- r
    'https://www.socks-proxy.net/', # -- r
    'https://www.proxy-list.download/HTTP',
    'https://www.proxylist4all.com/wp-admin/admin-ajax.php?action=getProxyList&request=',
    'https://proxy11.com/api/v3/demo',
    'https://www.coderduck.com/free-proxy-list',
    'http://nntime.com/proxy-list-0{page}.htm',
}

TARGET_DICT = {
    'www.duplichecker.com': 'www_duplichecker_com',
    'free-proxy.cz': 'free_proxy_cz',
    'free-proxy-list.com': 'free_proxy_list_com',
    'www.idcloak.com': 'www_idcloak_com',
    'list.proxylistplus.com': 'list_proxylistplus_com',
    'www.my-proxy.com': 'www_my_proxy_com',
    'proxy-list.org': 'proxy_list_org',
    'proxydb.net': 'proxydb_net',
    'www.proxynova.com': 'www_proxynova_com',
    'www.proxyrack.com': 'www_proxyrack_com',
    'www.proxyscan.io': 'www_proxyscan_io',
    'api.proxyscrape.com': 'api_proxyscrape_com',
    'scrapingant.com': 'scrapingant_com',
    'smallseotools.com': 'smallseotools_com',
    'www.sslproxies.org': 'www_sslproxies_org',
    'www.socks-proxy.net': 'www_socks_proxy_net',
    'www.proxy-list.download': 'www_proxy_list_download',
    'www.proxylist4all.com':'www_proxylist4all_com',
    'proxy11.com':'proxy11_com',
    'www.coderduck.com':'www_coderduck_com',
    'nntime.com':'nntime_com',
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''
PROXY_KEY = 'proxies'  # set

POOL = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, max_connections=80, decode_responses=True)
