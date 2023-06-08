#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Author:liamlee
@Contact:geektalk@qq.com
@Ide:PyCharm
@Time:2023/5/24 23:31
@Project:WeiboSpiderX
@File:user.py
@Desc:用户管道
"""
import json
from typing import Union, List

from WeiboSpiderX import constants
from WeiboSpiderX.bean.cache_user import CacheUser, CacheUserItem
from WeiboSpiderX.bean.user import UserItem
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.utils.tool import get_time_now, set_attr


class UserPipeline:

    def __init__(self, settings, server):
        self.settings = settings
        self.server = server

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        settings = crawler.settings
        server = crawler.spider.server
        return cls(settings, server)

    def process_item(self, item: dict, spider) -> Union[List[UserItem], dict]:
        if isinstance(item, dict) and item.get("user"):
            users = extractor_user(item["user"])
            for user in users:
                if self.server.hexists(constants.USER_KEY, user.idstr):
                    user_redis = json.loads(self.server.hget(constants.USER_KEY, user.idstr))

                    cache_user_redis = set_attr(user_redis, CacheUser())
                    cache_user_redis.now = set_attr(cache_user_redis.now, CacheUserItem())
                    cache_user_redis.now.user = set_attr(cache_user_redis.now.user, UserItem())

                    cache_user_list = []
                    for _ in cache_user_redis.list:
                        cache_user_item = set_attr(_, CacheUserItem())
                        cache_user_item.user = set_attr(cache_user_item.user, UserItem())
                        cache_user_list.append(cache_user_item)
                    cache_user_redis.list = cache_user_list

                    if cache_user_list[-1].user.screen_name != user.screen_name:
                        info = {"time": get_time_now(), "user": user.to_dict()}
                        cache_user_item = set_attr(info, CacheUserItem())
                        cache_user_item.user = set_attr(cache_user_item.user, UserItem())

                        cache_user_redis.now = cache_user_item
                        cache_user_redis.list.append(cache_user_item)
                        self.server.hset(constants.USER_KEY, user.idstr, cache_user_redis.to_json())
                else:

                    info = {"time": get_time_now(), "user": user.to_dict()}
                    cache_user_item = set_attr(info, CacheUserItem())

                    cache_user = CacheUser()
                    cache_user.now = cache_user_item
                    cache_user.list.append(cache_user_item)
                    self.server.hset(constants.USER_KEY, user.idstr, cache_user.to_json())
            return users
        return item
