# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

import time
import re
from scrapy.exceptions import DropItem


class BaiduPipeline(object):
    def process_item(self, item, spider):
        return item


'''class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['Question'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['Question'])
            return item'''


class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('baidu.txt', 'wb')
        self.fileDict = open('baiduDict.txt', 'wb')

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), encoding='utf-8', ensure_ascii=False).replace(" 评论 | 分享", "").replace("分享 评论 |","").strip() + "\n"
        #
        line = ""
        dictLine = ""
        if len(dict(item).values()) > 1:
            dictLine = dict(item)['name'].encode("utf-8") + "\n"
            line = dict(item)['animalText'].encode("utf-8") + "\n"
        # time.sleep(5)
        dictLine = dictLine.replace("_百度百科", "")
        dictLine = re.sub('（.*?）'.encode("utf-8"), '', dictLine.encode("utf-8"))
        # print dictLine
        # time.sleep(100)
        self.fileDict.write(dictLine)
        self.fileDict.flush()
        self.file.write(line)
        # time.sleep(1)
        return item


class WikiWriterPipeline(object):
    def __init__(self):
        self.file = open('wiki.txt', 'wb')

    def process_item(self, item, spider):
        # line = json.dumps(dict(item), encoding='utf-8', ensure_ascii=False).replace(" 评论 | 分享", "").replace("分享 评论 |","").strip() + "\n"
        #
        line = ""
        if len(dict(item).values()) > 0:
            line = dict(item)['content'].encode("utf-8")
        # time.sleep(5)
        # print dictLine
        # time.sleep(100)
        self.file.write(line)
        self.file.flush()
        # time.sleep(1)
        return item
