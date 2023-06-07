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
from WeiboSpiderX.bean.user import UserItem
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.utils.tool import get_time_now


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
                    old_user = json.loads(user_redis["list"][-1].get("user"))
                    if old_user.get("screen_name") != user.screen_name:
                        user_redis["user"] = user.to_json()
                        user_redis["list"].append({"user": user.to_json(), "time": get_time_now()})
                        self.server.hset(constants.USER_KEY, user.idstr, json.dumps(user_redis, ensure_ascii=False))
                else:
                    info = {"user": user.to_json(), "list": [{"user": user.to_json(), "time": get_time_now()}]}
                    self.server.hset(constants.USER_KEY, user.idstr, json.dumps(info, ensure_ascii=False))
            return users
        return item
