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
from typing import List, Dict

from scrapy.exceptions import IgnoreRequest
from scrapy_redis import get_redis_pool

from WeiboSpiderX import constants
from WeiboSpiderX.bean.cache import CacheItem
from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.utils.tool import set_attr


class Cache:
    server = get_redis_pool()
    cache = {}  # 全量采集的用户标志

    def set_redis(self, uid, value: CacheItem):
        """
        持续化缓存
        :param uid: 用户标识
        :param value: 缓存项
        """
        uid = str(uid)
        self.server.hset(constants.FULL_KEY, uid, value.to_json())
        self.cache[uid] = value

    def get_redis(self, uid) -> CacheItem:
        """
        获取缓存
        :param uid: 用户标识
        :return: 缓存项
        """
        uid = str(uid)
        value = json.loads(self.server.hget(constants.FULL_KEY, uid))
        cache_item = set_attr(value, CacheItem())
        self.cache[uid] = cache_item
        return cache_item

    def check_redis(self, uid) -> bool:
        """
        检查缓存是否存在
        :param uid: 用户标识
        :return: 是否存在缓存
        """
        return self.server.hexists(constants.FULL_KEY, str(uid))

    def get_cache(self, uid) -> CacheItem:
        """
        获取缓存，先从内存中查找，若不存在则从 Redis 中获取
        :param uid: 用户标识
        :return: 缓存项
        """
        uid = str(uid)
        if uid in self.cache:
            return self.cache[uid]
        return self.get_redis(uid)


class CacheFactory(Cache):

    @staticmethod
    def filter_blog_id(medias: List[MediaItem]) -> Dict[str, str]:
        """
        筛选博客编号
        :param medias: 媒体列表
        :return: {用户:博客编号}
        """
        b = defaultdict(set)
        for m in medias:
            b[m.blog.id].add(m.blog_id)
        return dict(b)

    def update_cache(self, medias: List[MediaItem]):
        """
        更新缓存信息
        :param medias:媒体列表
        :return:
        """
        for uid, blog_ids in self.filter_blog_id(medias).items():
            full = self.get_cache(uid)
            # 修改有效值
            full.real_total = len(full.blog_ids)

            # 首次添加
            if full.real_total == 0:
                full.real_total += len(blog_ids)
                self.set_redis(uid, full)

            # 其次添加
            elif full.real_total <= full.total and not full.is_end:
                full.real_total += len(blog_ids)
                self.set_redis(uid, full)

    def init_spider_record(self, request, response):
        """
        初始化爬虫记录器
        :param request:请求对象
        :param response:响应对象
        :return:
        """
        finder = JsonDataFinderFactory(response.text)

        total = finder.get_first_value("total")
        uid = request.meta.get("params", {}).get("uid")

        if not self.check_redis(uid):
            # 新博主，创建缓存项
            full = CacheItem()
            full.uid = uid
            full.total = total
            full.last_total = total
            self.set_redis(uid, full)
        else:
            # 已存在的博主，更新缓存项
            full = self.get_redis(uid)
            full.last_total = full.total
            full.total = total if total != 0 else full.total
            self.set_redis(uid, full)

    def request_filter(self, request):
        """
        全量采集请求过滤器
        :param request:请求对象
        :return:
        """
        uid = request.meta.get("params", {}).get("uid")

        if self.check_redis(uid):
            full = self.get_cache(uid)

            # 如果已经全量爬取完毕，则过滤请求
            if full.is_end and full.total == full.last_total:
                print(f"{uid}已经全量爬取...")
                raise IgnoreRequest("URL filtered: {}".format(request.url))

    def spider_record(self, completes, item):
        """
        爬虫记录器
        :param completes:已完成的下载列表
        :param item:当前处理的项目
        :return:
        """
        for media in item:
            uid = media.blog.id
            blog_id = media.blog_id
            url = media.url

            full = self.get_cache(uid)
            blog_ids = full.blog_ids

            # 根据url和是否存在blog_id添加
            if any(x.get("url") == url for x in completes) and blog_id not in blog_ids:
                blog_ids.append(blog_id)
                full.last_total += 1  # 计数
                self.set_redis(uid, full)
