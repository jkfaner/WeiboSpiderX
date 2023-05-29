#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/28 03:25
@Project:WeiboSpiderX
@File:cache.py
@Desc:
"""
import json
from collections import defaultdict
from typing import List

from scrapy.exceptions import IgnoreRequest
from scrapy_redis import get_redis

from WeiboSpiderX import constants
from WeiboSpiderX.bean.cache import CacheItem
from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.utils.tool import set_attr


class Cache:
    server = get_redis()
    cache = {}  # 全量采集的用户标志

    def set_redis(self, uid, value: CacheItem):
        """
        持续化缓存
        :param uid:
        :param value:
        :return:
        """
        if not isinstance(uid, str):
            uid = "{}".format(uid)
        self.server.hset(constants.FULL_KEY, uid, value.to_json())
        self.cache[uid] = value

    def get_redis(self, uid):
        """
        获取缓存
        :param uid:
        :return:
        """
        if not isinstance(uid, str):
            uid = "{}".format(uid)
        self.cache[uid] = set_attr(json.loads(self.server.hget(constants.FULL_KEY, uid)), CacheItem())
        return self.cache[uid]

    def check_redis(self, uid) -> bool:
        """
        检查缓存
        :param uid:
        :return:
        """
        return self.server.hexists(constants.FULL_KEY, uid)

    def get_cache(self, uid) -> CacheItem:
        """
        获取缓存
        :param uid:
        :return:
        """
        if not isinstance(uid, str):
            uid = "{}".format(uid)
        c = self.cache.get(uid, None)
        return c if c else self.get_redis(uid)


class CacheFactory(Cache):

    def update_cache(self, medias: List[MediaItem]):
        """
        添加缓存
        :param medias:
        :return:
        """

        # 筛选blog_id
        b = defaultdict(list)
        for m in medias:
            uid = m.blog.id
            blog_id = m.blog_id
            if blog_id not in b[uid]:
                b[uid].append(blog_id)
        blogs_item = dict(b)

        for uid, blog_ids in blogs_item.items():
            full = self.get_cache(uid)
            # 首次添加
            if full.real_total == 0:
                full.real_total = full.real_total + len(blogs_item[uid])
                self.set_redis(uid, full)

            # 其次添加
            elif full.real_total <= full.total and not full.is_end:
                full.real_total = full.real_total + len(blogs_item[uid])
                self.set_redis(uid, full)

    def init_spider_record(self, request, response):
        """
        初始化爬虫记录器
        :param request:
        :param response:
        :return:
        """
        # 记录当前博主所有博客量
        finder = JsonDataFinderFactory(response.text)
        #  total:微博数量
        #  real_total：实际值
        #  微博接口问题 该数值比实际要大 why?
        total = finder.get_first_value("total")
        uid = request.meta.get("params", {}).get("uid")

        # 持续化缓存
        if not self.check_redis(uid):
            full = CacheItem()
            full.uid = uid
            full.total = total
            full.last_total = total
            self.set_redis(uid, full)  # 持续化缓存
        else:
            full = self.get_redis(uid)
            full.last_total = full.total
            full.total = full.total if total == 0 else total  # 刷新博客数
            self.set_redis(uid, full)  # 持续化缓存

    def request_filter(self, request):
        """
        全量采集请求过滤器
        :param request:
        :return:
        """
        uid = request.meta.get("params", {}).get("uid")
        if self.check_redis(uid):
            full = self.get_cache(uid)
            if full.is_end and full.total == full.last_total:
                print(f"{uid}已经全量爬取...")
                raise IgnoreRequest("URL filtered: {}".format(request.url))

    def spider_record(self, completes, item):
        """
        爬虫记录器
        :param completes:
        :param item:
        :return:
        """
        for media in item:
            uid = media.blog.id
            blog_id = media.blog_id
            url = media.url

            full = self.get_cache(uid)
            blog_ids = full.blog_ids

            # 根据url和是否存在blog_id添加
            for x in completes:
                if x.get("url") == url and blog_id not in blog_ids:
                    blog_ids.append(blog_id)
                    full.last_total += 1  # 计数
                    self.set_redis(uid, full)
                    break  # 添加之后不会再次添加
