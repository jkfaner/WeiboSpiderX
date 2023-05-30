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
from typing import Union, List

from WeiboSpiderX import constants
from WeiboSpiderX.bean.user import UserItem
from WeiboSpiderX.extractor.wb_extractor import extractor_user


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
                self.server.hset(constants.USER_KEY, user.idstr, user.to_json())
            return users
        return item
