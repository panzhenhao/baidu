# coding:utf-8
# scrapy爬虫百度知道数据
import sys
import json
import re
import os
import string
from urllib import quote
from pyquery import PyQuery as pq
import time
import types
import re

reload(sys)
sys.setdefaultencoding('utf-8')
import scrapy
from scrapy import Request
from baidu.items import BaiduItem


# url_set=set()
# import sqlite3
class rsSpider(scrapy.spiders.Spider):  # 该类继承自 scrapy 中的 spider
    name = "baike"  # 将该爬虫命名为 “百科”，在执行爬虫时对应指令将为： scrapy crawl baike
    global url_set
    url_set = set()
    download_delay = 1  # 只是用于控制爬虫速度的，1s/次，可以用来对付反爬虫

    allowed_domains = ["baike.baidu.com"]  # 允许爬取的作用域
    # url_first = 'http://zhidao.baidu.com/question/'   #用于之后解析域名用的短字符串

    start_urls = ["http://baike.baidu.com/view/65942.htm"
                  "http://baike.baidu.com/view/27934.htm",
                  "http://baike.baidu.com/view/1975041.htm",
                  "http://baike.baidu.com/view/33311.htm",
                  "http://baike.baidu.com/view/65992.htm",
                  "http://baike.baidu.com/view/30105.htm"
                  ]  # 脊髓动物

    def parse(self, response):
        pageName = response.xpath('//title/text()').extract()[0]  # 解析爬取网页中的名称
        pageUrl = "http://baike.baidu.com/view/" + \
                  ''.join(response.xpath("//div[@class='anchor-list'][1]/a[2]").re('name="(.*?)"')).split("_")[
                      0].replace("sub", "") + ".htm"  # 解析爬取网页的 url，并不是直接使用函数获取，那样会夹杂乱码
        # pageUrl = ''.join(response.xpath("//div[@class='anchor-list'][1]/a[2]").re('name="(.*?)"')).split("_")[0].replace("sub", "")
        pageHtml = response.xpath("//html").extract()[0]  # 获取网页html
        # print "***********************************************************************************"
        # print pageName
        # print type(pageUrl)
        print "pageUrl:", pageUrl
        # print "***************************************************************"
        # print pageHtml
        # time.sleep(1)
        # judge whether pageUrl in cUrl
        if pageUrl in self.start_urls:
            # 增加一个求hash编码的过程
            if pageUrl in url_set:  # 若当前Url已经爬过
                pass
            else:  # 否则，将信息爬入数据库
                url_set.add(pageUrl)
                item = BaiduItem()
                try:
                    pq_content = pq(pageHtml.replace("&nbsp;", "")
                                    .replace("\t", "").replace("\r\n", ""))
                    acontent = re.sub('[a-zA-Z]|\?| |？', '', pq_content("div.para").text())
                    # print acontent
                    acontent = re.sub('（.*?）'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\(.*?\)'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('【.*?】'.encode("utf-8"), '', acontent.encode("utf-8"))
                    acontent = re.sub('\[.*?\]'.encode("utf-8"), '', acontent.encode("utf-8"))
                    openTag = str(pq_content("div#open-tag").text()).encode("utf-8")
                    flag = 0  # 查看开发标签是否为需要额类别
                    # print openTag
                    if "动物".encode("utf-8") in openTag:
                        flag = 1
                    # print 'acontent:',acontent
                    # time.sleep(100)
                    if len(acontent) > 0 and flag == 1:
                        item['animalText'] = str(acontent)
                        item['name'] = str(pageName).encode("utf-8")
                        # fout.flush()
                except Exception, e:
                    print e
                # print item
                yield item
                # print pageName, pageUrl, pageHtml
        else:  # 此时进入的非 url 网页一定是没有爬取过的（因为深入start_url之后的网页都会先进行判断，在爬取，在下面的for循环中判断）
            # url_set.add(pageUrl)
            item = BaiduItem()
            # print "else operation"
            # time.sleep(1)
            try:
                pq_content = pq(pageHtml.replace("&nbsp;", "")
                                .replace("\t", "").replace("\r\n", ""))
                acontent = re.sub('[a-zA-Z]|\?| |？', '', pq_content("div.para").text())
                # print acontent
                acontent = re.sub('（.*?）'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\(.*?\)'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('【.*?】'.encode("utf-8"), '', acontent.encode("utf-8"))
                acontent = re.sub('\[.*?\]'.encode("utf-8"), '', acontent.encode("utf-8"))
                openTag = str(pq_content("div#open-tag").text()).encode("utf-8")
                flag = 0;  # 查看开发标签是否为需要额类别
                # print openTag
                if "动物".encode("utf-8") in openTag:
                    flag = 1
                # print 'acontent:',acontent
                # time.sleep(100)
                if len(acontent) > 0 and flag == 1:
                    item['animalText'] = str(acontent)
                    item['name'] = str(pageName)
                    # fout.flush()
            except Exception, e:
                print e
            # print item
            yield item
            # print pageName, pageUrl, pageHtml
        # 相当于递归调用
        for sel in response.xpath('//a').re('href="(/view/.*?.htm)'):  # 抓出所有该网页的延伸网页，进行判断并对未爬过的网页进行爬取
            sel = "http://baike.baidu.com" + sel  # 解析出延伸网页的url
            # print sel
            # print len(url_set)
            if sel not in url_set:  # 若不在，则对其继续进行爬取
                url_set.add(sel)
                # print "set length:",len(url_set)
                yield Request(url=sel, callback=self.parse)
