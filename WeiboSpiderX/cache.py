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
import logging
from collections import defaultdict
from typing import List, Dict

from scrapy.exceptions import IgnoreRequest
from scrapy_redis import get_redis_pool

from WeiboSpiderX import constants
from WeiboSpiderX.bean.cache import CacheItem
from WeiboSpiderX.bean.media import MediaItem
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.utils.tool import set_attr, get_time_now

logger = logging.getLogger(__name__)


class Cache:
    server = get_redis_pool()

    def set_redis(self, uid, value: CacheItem):
        """
        持续化缓存
        :param uid: 用户标识
        :param value: 缓存项
        """
        self.server.hset(constants.FULL_KEY, str(uid), value.to_json())

    def get_redis(self, uid) -> CacheItem:
        """
        获取缓存
        :param uid: 用户标识
        :return: 缓存项
        """
        value = json.loads(self.server.hget(constants.FULL_KEY, str(uid)))
        return set_attr(value, CacheItem())

    def check_redis(self, uid) -> bool:
        """
        检查缓存是否存在
        :param uid: 用户标识
        :return: 是否存在缓存
        """
        return self.server.hexists(constants.FULL_KEY, str(uid))


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
            full = self.get_redis(uid)

            # 如果已经全量爬取完毕，则过滤请求
            if full.is_end and full.total == full.last_total:
                logger.info(f"{uid}已经全量爬取...")
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

            full = self.get_redis(uid)
            blogs_id = [_.get("blog_id") for _ in full.blog_ids]

            # url必须与存在该博客中
            if any(x.get("url") == url for x in completes) and blog_id not in blogs_id:
                full.blog_ids.append({"time": get_time_now(), "blog_id": blog_id})
                full.real_total += 1  # 计数
                self.set_redis(uid, full)


class CacheHelper(Cache):
    """开发时使用"""

    def load_redis(self, name, batch_size=50):
        """
        加载redis数据
        :param name:
        :param batch_size:
        :return:
        """
        batch = []
        # 游标初始值为0
        cursor = 0
        # 遍历哈希表
        while True:
            # 使用 HSCAN 命令获取指定哈希表中的键值对
            cursor, data = self.server.hscan(name, cursor)
            # 遍历返回的键值对
            for key in data.keys():
                media = self.server.hget(name, key)
                if media:
                    batch.append(json.loads(media))
                    if len(batch) >= batch_size:
                        yield batch
                        batch = []

            # 如果游标为0，表示遍历结束
            if cursor == 0:
                break

        if batch:
            yield batch
