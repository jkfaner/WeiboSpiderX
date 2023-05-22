import json
import time
from abc import ABC
from typing import List
from urllib.parse import urlencode

import scrapy
from scrapy.utils.project import get_project_settings
from scrapy_redis import get_redis
from scrapy_redis.spiders import RedisSpider

from WeiboSpiderX import constants
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.utils.tool import read_json_file

# 获取项目设置参数
settings = get_project_settings()
SPIDER_BLOG_TYPE = settings.get('SPIDER_BLOG_TYPE')


class WeiboAPI(object):

    def __init__(self):
        self.groups_url = "https://weibo.com/ajax/profile/getGroups"
        self.group_members_url = "https://weibo.com/ajax/profile/getGroupMembers"
        self.user_blog_url = "https://weibo.com/ajax/statuses/mymblog"
        self.user_info_url = "https://weibo.com/ajax/profile/info"
        self.user_info_detail_url = "https://weibo.com/ajax/profile/detail"
        self.user_friends_url = "https://weibo.com/ajax/friendships/friends"
        self.user_follow_content_url = "https://weibo.com/ajax/profile/followContent"
        self.cookie = None
        system_config = read_json_file("./system-config.json")
        self.original = system_config.get("original")
        self.forward = system_config.get("forward")
        self.filter_uids = []
        # self.filter_uids = self.get_filter_user()

    def get_filter_user(self):
        original_users = [user.split("/")[-1] for user in self.original]
        forward_users = [user.split("/")[-1] for user in self.forward]
        if SPIDER_BLOG_TYPE == constants.BLOG_FILTER_ORIGINAL:
            users = list(set(original_users))
        elif SPIDER_BLOG_TYPE == constants.BLOG_FILTER_FORWARD:
            users = list(set(forward_users))
        else:
            original_users.extend(forward_users)
            users = list(set(original_users))
        for user in users:
            print("允许下载:{}".format(user))
        return users

    def get_api(self):
        attributes = [
            self.user_blog_url,
            self.user_info_url,
            self.user_info_detail_url,
            self.user_friends_url,
            self.user_follow_content_url
        ]
        return attributes

    def get_cookie(self):
        if self.cookie is None:
            # 添加cooke
            cookie = get_redis().hget(constants.LOGIN_KEY, constants.SPIDER_UID)
            self.cookie = json.loads(cookie)
            return self.cookie
        return self.cookie


class WeiboSpider(WeiboAPI, RedisSpider, ABC):
    name = "weibo"

    def start_requests(self):
        """
        爬虫入口
        :return:
        """
        return self.get_groups()

    def get_groups(self):
        """
        获得分组
        :return:
        """
        params = {"showBilateral": 1}
        yield scrapy.Request(
            url=f'{self.groups_url}?{urlencode(params)}',
            cookies=self.get_cookie(),
            meta={"url": self.groups_url, "params": params},
            callback=self.get_group_members
        )

    def get_group_members(self, response):
        """
        获得分组数据
        :return:
        """
        if response.meta.get("url") == self.groups_url:
            # 第一次获取分组下的用户
            finder = JsonDataFinderFactory(response.text, mode="value")
            group_items = finder.get_same_level(constants.SPIDER_GROUP)
            params = {"list_id": group_items[0].get("idstr"), "page": 1}

            yield scrapy.Request(
                url=f'{self.group_members_url}?{urlencode(params)}',
                cookies=self.get_cookie(),
                meta={"url": self.group_members_url, "params": params},
                callback=self.get_group_members
            )
        else:
            # 其他次数获取分组用户数据
            finder = JsonDataFinderFactory(response.text)
            users = finder.find_first_value("users")
            if users:
                time.sleep(2)

                # 获取用户
                params = response.meta.get("params")
                params["page"] = params["page"] + 1
                yield scrapy.Request(
                    url=f'{self.group_members_url}?{urlencode(params)}',
                    cookies=self.get_cookie(),
                    meta={"url": self.group_members_url, "params": params},
                    callback=self.get_group_members
                )

                # 获取博客
                for user in extractor_user(response.text):
                    params = {"uid": user.idstr, "page": 1, "since_id": "", "feature": 0}
                    yield scrapy.Request(
                        url=f'{self.user_blog_url}?{urlencode(params)}',
                        cookies=self.get_cookie(),
                        meta={"url": self.user_blog_url, "params": params},
                        callback=self.get_blogs
                    )

    def get_blogs(self, response):
        """
        获取博客
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text)
        if finder.exist_key("list"):
            yield dict(blog=response.text)

            time.sleep(2)

            # 获取博客
            since_id = finder.get_first_value("since_id")
            query = response.meta["params"]
            params = {"uid": query["uid"], "page": query["page"] + 1, "since_id": since_id, "feature": 0}
            yield scrapy.Request(
                url=f'{self.user_blog_url}?{urlencode(params)}',
                cookies=self.get_cookie(),
                meta={"url": self.user_blog_url, "params": params},
                callback=self.get_blogs
            )
