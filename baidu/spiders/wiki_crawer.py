# coding:utf-8
# scrapy爬虫百度知道数据
import re
import sys
import time

from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from scrapy import Request
from baidu.items import WikiItem


# url_set=set()
# import sqlite3
class rsSpider(scrapy.spiders.Spider):  # 该类继承自 scrapy 中的 spider
    name = "wiki"  # 将该爬虫命名为 “wiki”，在执行爬虫时对应指令将为： scrapy crawl wiki
    global url_set
    url_set = set()
    # download_delay = 2  # 只是用于控制爬虫速度的，1s/次，可以用来对付反爬虫

    allowed_domains = ["en.wikipedia.org"]  # 允许爬取的作用域
    # url_first = 'http://zhidao.baidu.com/question/'   #用于之后解析域名用的短字符串

    start_urls = [ "https://en.wikipedia.org/wiki/Animal"
                   #"https://en.wikipedia.org/wiki/Daily_News_and_Analysis"
                  ]  # 动物

    def parse(self, response):
        pageName = response.xpath('//*[@id="firstHeading"]/text()') #.extract()[0]  # 解析爬取网页中的名称
        if len(pageName) == 0:
            pageName = str(response.xpath('//*[@id="firstHeading"]/i').extract()[0])[3:-4]
        else:
            pageName = str(pageName.extract()[0])
        pageUrl = "https://en.wikipedia.org/wiki/" + pageName  # 解析爬取网页的 url，并不是直接使用函数获取，那样会夹杂乱码
        pageHtml = response.xpath("//html").extract()[0]  # 获取网页html
        # print "**************************************************************************"
        # print pageName
        # print type(pageUrl)
        # print "pageUrl:",pageUrl
        # print "******************************************************"
        # print pageHtml
        # time.sleep(100)
        # judge whether pageUrl in cUrl
        if pageUrl in self.start_urls:
            # 增加一个求hash编码的过程
            if pageUrl in url_set:  # 若当前Url已经爬过
                pass
            else:  # 否则，将信息爬入数据库
                url_set.add(pageUrl)
                item = WikiItem()
                try:
                    pq_content = pq(pageHtml.replace("&nbsp;", "")
                                    .replace("\t", "").replace("\r\n", ""))
                    acontent = pq_content("p").text()
                    acontent = re.sub('\(.*?\)'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\[.*?\]'.encode("utf-8"), '', acontent.encode("utf-8"))
                    # acontent = re.sub('（.*?）'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub(',|\\.|:|\\;'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\\".*?\\"'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\'.*?\''.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\'?'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\\ +'.encode("utf-8"), ' ', acontent.encode("utf-8"))
                    acontent = acontent.lower()
                    # print acontent
                    # time.sleep(100)
                    openTag = str(pq_content("#mw-normal-catlinks").text()).encode("utf-8").lower()
                    flag = 0  # 查看开发标签是否为需要额类别
                    print openTag
                    if "animals".encode("utf-8") in openTag:
                        flag = 1
                    # print 'flag:', flag
                    # time.sleep(100)
                    if len(acontent) > 0 and flag == 1:
                        item['content'] = str(acontent)
                        # fout.flush()
                except Exception, e:
                    print e
                # print item
                yield item
                # print pageName, pageUrl, pageHtml
        else:  # 此时进入的非 url 网页一定是没有爬取过的（因为深入start_url之后的网页都会先进行判断，在爬取，在下面的for循环中判断）
            url_set.add(pageUrl)
            item = WikiItem()
            # print "else operation"
            # time.sleep(1)
            try:
                pq_content = pq(pageHtml.replace("&nbsp;", "")
                                .replace("\t", "").replace("\r\n", ""))
                acontent = pq_content("p").text()
                acontent = re.sub('\(.*?\)'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\[.*?\]'.encode("utf-8"), '', acontent.encode("utf-8"))
                # acontent = re.sub('（.*?）'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub(',|\\.|:|\\;'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\\".*?\\"'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\'.*?\''.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\'?'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\\ +'.encode("utf-8"), ' ', acontent.encode("utf-8"))
                acontent = acontent.lower()
                # print acontent
                # time.sleep(100)
                openTag = str(pq_content("#mw-normal-catlinks").text()).encode("utf-8").lower()
                flag = 0  # 查看开发标签是否为需要额类别
                print openTag
                if "animals".encode("utf-8") in openTag:
                    flag = 1
                # print 'flag:', flag
                # time.sleep(100)
                if len(acontent) > 0 and flag == 1:
                    item['content'] = str(acontent)
                    # fout.flush()
            except Exception, e:
                print e
                # print item
            yield item
        # 相当于递归调用
        for sel in response.xpath('//a').re('href="(/wiki/.*?\")'):  # 抓出所有该网页的延伸网页，进行判断并对未爬过的网页进行爬取
            sel = "https://en.wikipedia.org" + str(sel)[:-1]  # 解析出延伸网页的url
            # print sel
            # time.sleep(100)
            # print len(url_set)
            if sel not in url_set:  # 若不在，则对其继续进行爬取
                # url_set.add(sel)
                # print "set length:",len(url_set)
                yield Request(url=sel, callback=self.parse)
