# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.cookies import CookieJar
from scrapy.http import Request
from chouti import settings

class ChouticookiejarSpider(scrapy.Spider):
    name = 'chouticookiejar'
    allowed_domains = ['chouti.com']
    start_urls = ['http://chouti.com/']

    cookie_dict={}

    url_set=set()

    def start_requests(self):
        url = 'http://dig.chouti.com/'
        yield Request(url,callback=self.login)   # 第一次请求 获取 cookie

    def login(self,response):
        url = 'http://dig.chouti.com/login'
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response,response.request)

        for k,v in cookie_jar._cookies.items():
            for i,j in v.items():
                for m,n in j.items():
                    self.cookie_dict[m]=n.value

        yield Request(url,
                      method="POST",
                      headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                      body='phone=86%s&password=%s&oneMonth=1'%(settings.ACCOUNT,settings.PWD),
                      cookies=self.cookie_dict,
                      callback=self.check_login)

    def check_login(self,response):
        url = "http://dig.chouti.com/"

        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response,response.request)

        for k,v in cookie_jar._cookies.items():
            for i,j in v.items():
                for m,n in j.items():
                    self.cookie_dict[m]=n.value
        yield Request(url=url,callback=self.parse_index,cookies=self.cookie_dict,dont_filter=True)


    def parse_index(self,response):


        page_list = response.xpath('//*[@id="dig_lcpage"]/ul/li/a/@href').extract()

        for page_url in page_list:

            page_url = response.urljoin(page_url)

            if page_url in self.url_set:
                pass

            else:
                self.url_set.add(page_url)
                yield Request(page_url,callback=self.parse_index,cookies=self.cookie_dict)

        vote_idList =  response.xpath('//*[@id="content-list"]//img/@lang').extract()
        for vote_id in vote_idList:
            vote_url = "http://dig.chouti.com/link/vote?linksId="+vote_id
            yield Request(vote_url,cookies=self.cookie_dict,method="POST",callback=self.result)

    def result(self,response):
        print(response.text)