import json
import logging
import time
from abc import ABC
from typing import List
from urllib.parse import urlencode

import scrapy
from scrapy_redis import get_redis
from scrapy_redis.spiders import RedisSpider

from WeiboSpiderX import constants
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.extractor.wb_extractor import extractor_user
from WeiboSpiderX.utils.tool import parse_query_params, read_json_file
from scrapy.utils.project import get_project_settings

# 获取项目设置参数
settings = get_project_settings()
SPIDER_BLOG_TYPE = settings.get('SPIDER_BLOG_TYPE')


class WeiboAPI(object):

    def __init__(self):
        self.user_blog_url = "https://weibo.com/ajax/statuses/mymblog"
        self.user_info_url = "https://weibo.com/ajax/profile/info"
        self.user_info_detail_url = "https://weibo.com/ajax/profile/detail"
        self.user_friends_url = "https://weibo.com/ajax/friendships/friends"
        self.user_follow_content_url = "https://weibo.com/ajax/profile/followContent"
        self.cookie = None
        system_config = read_json_file("./src/resource/system-config.json")
        self.original = system_config.get("original")
        self.forward = system_config.get("forward")
        self.filter_uids = self.get_filter_user()

    @staticmethod
    def parse_user(users: List) -> List:
        return [user.split("/")[-1] for user in users]

    def get_filter_user(self):
        original_users = self.parse_user(self.original)
        forward_users = self.parse_user(self.forward)
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
        # 获取用户关注
        params = dict(page=1, uid=constants.SPIDER_UID)
        url = f'{self.user_friends_url}?{urlencode(params)}'
        yield scrapy.Request(url=url, cookies=self.get_cookie(), callback=self.get_user_follow)

    def get_user_follow(self, response):
        """
        获取用户关注
        :param response:
        :return:
        """
        finder = JsonDataFinderFactory(response.text)
        if finder.exist_key("users"):
            for uid in finder.find_all_values("idstr"):
                if uid in self.filter_uids:
                    yield {'user': response.text}
                    time.sleep(2)
                    # 获取用户
                    params = parse_query_params(response.url)
                    params = dict(page=int(params['page']) + 1, uid=params['uid'])
                    url = f'{self.user_friends_url}?{urlencode(params)}'
                    yield scrapy.Request(url=url, cookies=self.get_cookie(), callback=self.get_user_follow)

                    # 获取博客
                    for user in extractor_user(response.text):
                        params = dict(uid=user.idstr, page=1, since_id="", feature=0)
                        url = f'{self.user_blog_url}?{urlencode(params)}'
                        yield scrapy.Request(url=url, cookies=self.get_cookie(), callback=self.get_blogs)

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
            params = parse_query_params(response.url)
            params = dict(uid=params['uid'], page=int(params['page']) + 1, since_id=since_id, feature=0)
            url = f'{self.user_blog_url}?{urlencode(params)}'
            yield scrapy.Request(url=url, cookies=self.get_cookie(), callback=self.get_blogs)
