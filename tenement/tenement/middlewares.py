# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import time
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class TenementSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TenementDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SeleniumMiddlewares(object):
    """
    Selenium中间件，用来使用浏览器模拟下载请求,注意打开setting中的DOWNLOADER_MIDDLEWARES
    才能生效
    """

    def __init__(self):
        #初始化一个FireFox实例
        self.option = Options()
        self.option.add_argument('-headless')
        self.browser = webdriver.Firefox(executable_path="E:/python/geckodriver",
                                         firefox_options=self.option)

    def process_request(self, request, spider):
        """
        该方法在中间件被激活的时候系统自动调用，处理request请求
        spider.name可以区分不同的爬虫
        :param request:
        :param spider:
        :return:
        """
        #使用元数据meta重的page判断是否是分页请求
        if int(request.meta["page"]) > 0:
            #将页面滚动到最后
            self.browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
            #找到"下一页"并模拟点击
            page = self.browser.find_element_by_xpath('//a[@class="next"]')
            page.click()
            time.sleep(10)
        else:
            # 正常页直接执行下载
            self.browser.get(request.url)

        time.sleep(3)
        #生成HtmlResponse，将浏览器模拟的下载结果返回给我们的spider，结果存在self.browser.page_source中
        #结果是整个页面的html代码
        return HtmlResponse(url=self.browser.current_url,body=self.browser.page_source, encoding="utf-8",
                            request=request)


import random
PROXIES = ['http://183.207.95.27:80', 'http://111.6.100.99:80']


class ProxyMiddleware(object):
    '''
    设置Proxy
    '''
    def process_request(self, request, spider):
        ip = random.choice(PROXIES)
        request.meta['proxy'] = ip


class MyUserAgentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('USER_AGENT')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers['User-Agent'] = agent
