import json
import sys
import time
from abc import ABC
from urllib.parse import urlencode

import scrapy
from DecryptLogin.core import weibo
from requests.utils import dict_from_cookiejar
from scrapy_redis.spiders import RedisSpider

from WeiboSpiderX import constants
from WeiboSpiderX.extractor.extractor import JsonDataFinderFactory
from WeiboSpiderX.extractor.wb_extractor import extractor_user


class WeiboSpider(RedisSpider, ABC):
    name = "weibo"

    def __init__(self, *args, **kwargs):
        super(WeiboSpider).__init__(*args, **kwargs)
        self.groups_url = "https://weibo.com/ajax/profile/getGroups"
        self.group_members_url = "https://weibo.com/ajax/profile/getGroupMembers"
        self.user_blog_url = "https://weibo.com/ajax/statuses/mymblog"
        self.user_info_url = "https://weibo.com/ajax/profile/info"
        self.user_info_detail_url = "https://weibo.com/ajax/profile/detail"
        self.user_friends_url = "https://weibo.com/ajax/friendships/friends"
        self.user_follow_content_url = "https://weibo.com/ajax/profile/followContent"
        self.api_list = self.get_api()
        self.header = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,da;q=0.7,zh-TW;q=0.6",
        }
        self.settings = kwargs.get('settings')
        self.uid = None

    def get_api(self):
        attributes = [
            self.user_blog_url, self.user_info_url,
            self.user_info_detail_url, self.user_friends_url,
            self.groups_url, self.group_members_url, self.user_follow_content_url,
        ]
        return attributes

    # @classmethod
    # def from_crawler(cls, crawler, *args, **kwargs):
    #     spider = super(WeiboSpider, cls).from_crawler(crawler, *args, **kwargs)
    #     spider.settings = crawler.settings
    #     return spider

    def parse_login(self, response):
        """
        :param response:
        :return:
        """
        if response.url != response.meta["url"]:
            if response.url not in self.api_list:
                self.refresh_cookie()

    def get_cookie(self):
        self.uid = self.settings.get("SPIDER_UID")
        if self.server.hexists(constants.LOGIN_KEY, self.uid):
            cookie = self.server.hget(constants.LOGIN_KEY, self.uid)
            return json.loads(cookie)
        return self.refresh_cookie()

    def refresh_cookie(self):
        result, session = weibo().login()
        uid = result["uid"]
        if uid != self.uid:
            sys.exit("当前登录用户与设置用户不一致！")
        cookie = dict_from_cookiejar(session.cookies)
        self.server.hset(constants.LOGIN_KEY, self.uid, json.dumps(cookie))
        return cookie

    def request(self, raw_url, params, callback):
        """
        获取request
        :param raw_url: 不带任何参数的url
        :param params: 请求参数
        :param callback: 回调方法
        :return:
        """
        url = f'{raw_url}?{urlencode(params)}'
        meta = {
            "url": url,
            "raw_url": raw_url,
            "params": params,
            "callback": callback
        }
        cookies = self.get_cookie()
        request = scrapy.Request(url=url, cookies=cookies, meta=meta, callback=callback)
        return request

    def start_requests(self):
        """
        爬虫入口
        :return:
        """
        return self.process_groups()

    def process_groups(self):
        """
        获得分组
        :return:
        """
        params = {"showBilateral": 1}
        # yield self.request(raw_url=self.groups_url, params=params, callback=self.process_group_members)
        raw_url = self.groups_url
        callback = self.process_group_members
        url = f'{raw_url}?{urlencode(params)}'
        meta = {
            "url": url,
            "raw_url": raw_url,
            "params": params,
            "callback": callback
        }
        cookies = self.get_cookie()
        request = scrapy.Request(url=url, cookies=cookies, meta=meta, callback=callback)
        yield request

    def process_group_members(self, response):
        """
        获得分组数据
        :return:
        """
        self.parse_login(response)

        if response.meta.get("url") == self.groups_url:
            # 第一次获取分组下的用户
            finder = JsonDataFinderFactory(response.text, mode="value")
            group_items = finder.get_same_level(self.settings.get("SPIDER_GROUP"))
            params = {"list_id": group_items[0].get("idstr"), "page": 1}
            yield self.request(self.group_members_url, params, self.process_group_members)

        else:
            # 其他次数获取分组用户数据
            finder = JsonDataFinderFactory(response.text)
            users = finder.find_first_value("users")
            if users:
                time.sleep(2)

                # 获取用户
                params = response.meta.get("params")
                params["page"] = params["page"] + 1
                yield self.request(self.group_members_url, params, self.process_group_members)

                # 获取博客
                for user in extractor_user(response.text):
                    params = {"uid": user.idstr, "page": 1, "since_id": "", "feature": 0}
                    yield self.request(self.user_blog_url, params, self.process_blogs)

    def process_blogs(self, response):
        """
        获取博客
        :param response:
        :return:
        """
        self.parse_login(response)

        finder = JsonDataFinderFactory(response.text)
        if finder.exist_key("list"):
            yield dict(blog=response.text)

            time.sleep(2)

            # 获取博客
            since_id = finder.get_first_value("since_id")
            if since_id:
                query = response.meta["params"]
                params = {"uid": query["uid"], "page": query["page"] + 1, "since_id": since_id, "feature": 0}
                yield self.request(self.user_blog_url, params, self.process_blogs)
