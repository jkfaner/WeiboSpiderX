#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/27 19:10
@Project:WeiboSpiderX
@File:flow.py
@Desc:url过滤中间件
"""

from WeiboSpiderX.cache import CacheFactory


class URLFilterMiddleware(CacheFactory):

    def __init__(self, uid):
        super(URLFilterMiddleware, self).__init__()
        self.uid = uid

    @classmethod
    def from_crawler(cls, crawler):
        uid = crawler.settings.get('SPIDER_UID')
        return cls(uid)

    def process_response(self, request, response, spider):
        raw_url = request.meta.get("raw_url")
        if spider.name == "weibo":
            if raw_url != spider.user_blog_url:
                return response
        if response.status == 414:
            return response
        self.init_spider_record(request, response)
        self.request_filter(request)
        return response
