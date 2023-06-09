#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/6/7 15:54
@Project:WeiboSpiderX
@File:refresh.py
@Desc:
"""
from abc import ABC

import scrapy
from scrapy_redis.spiders import RedisSpider

from WeiboSpiderX.aop import ScrapyLogger
from WeiboSpiderX.cache import Cache
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.utils.tool import requestQuery


class RefreshWeibo(RedisSpider, ABC):
    name = "refresh"

    def __init__(self, **kwargs):
        super(RefreshWeibo, self).__init__()
        self.settings = kwargs.get('settings')
        self.groups_url = "https://weibo.com/ajax/profile/getGroups"

        self.groupstimeline_url = "https://weibo.com/ajax/feed/groupstimeline"
        self.list_id = ""
        self.refresh_times = 0
        self.refresh_max_times = 5

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(RefreshWeibo, cls).from_crawler(crawler, *args, **kwargs)
        spider.settings = crawler.settings
        return spider

    def start_requests(self):
        return self.process_groups()

    @ScrapyLogger(start={"info": "获取分组..."})
    def process_groups(self):
        """
        获得分组
        :return:
        """
        params = {"showBilateral": 1}
        item = requestQuery(self.groups_url, params, self.parse_groups)
        yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    @ScrapyLogger(start={"info": "首次获取分组下的博主..."})
    def parse_groups(self, response):
        """
        解析分组
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text, mode="value")
        group_items = finder.get_same_level(self.settings.get("SPIDER_GROUP"))
        self.list_id = group_items[0].get("idstr")
        return self.refresh_group(self.list_id)

    def refresh_group(self, group_id):
        params = {"list_id": group_id, "refresh": 4, "fast_refresh": 1, "count": 25}
        item = requestQuery(raw_url=self.groupstimeline_url, params=params, callback=self.process_groups_timeline)
        yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)

    def process_groups_timeline(self, response):
        finder = JsonDataFinderFactory(response.text)
        max_id_str = finder.find_first_value("max_id_str")
        if max_id_str:

            yield {"refresh": response.text}
            self.refresh_times += 1
            if self.refresh_times <= self.refresh_max_times:
                params = response.meta.get("params")
                params["max_id"] = max_id_str
                item = requestQuery(self.groupstimeline_url, params, self.process_groups_timeline)
                yield scrapy.Request(url=item.url, meta=item.meta, callback=item.callback)
            else:
                self.logger.info(f"当前已经刷新{self.refresh_times}次，达到最大刷新次数[{self.refresh_max_times}]，将从头开始刷新...")
        else:
            self.logger.info(f"无刷新数据...")
